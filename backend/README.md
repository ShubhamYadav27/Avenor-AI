# Avenor — Predictive Revenue Intelligence Backend

> Know who is about to buy, why, and what to say — before any competitor does.

Avenor is an AI-powered B2B revenue intelligence platform. It monitors companies for buying signals, scores them against your ICP, generates Account Intelligence Feeds, and learns from win/loss outcomes to improve predictions over time.

This repository is **Phase 4.1: Intelligence Backend** — the FastAPI modular monolith that powers the entire platform.

---

## What this system does

1. **Ingests signals** — hiring activity, funding rounds, tech changes, leadership changes, and news mentions for companies in your ICP universe
2. **Scores accounts** — composite signal scoring with ICP matching, recency decay, and combination bonuses
3. **Predicts buying windows** — classifies accounts as HOT (0–30d), WARM (30–60d), WATCH (60–90d), or COLD
4. **Generates intelligence** — GPT-4o produces plain-English signal summaries and recommended outreach angles per account
5. **Captures outcomes** — HubSpot webhook integration and manual logging feed win/loss data back into the model
6. **Learns over time** — weekly model recalibration updates signal weights from outcome data, improving accuracy with every customer

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                External Data Sources                │
│  Apollo · Crunchbase · BuiltWith · News · HubSpot  │
└────────────────────┬────────────────────────────────┘
                     │ batch every 6h
┌────────────────────▼────────────────────────────────┐
│              Signal Ingestion Workers               │
│         apollo_collector · news_collector           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                 PostgreSQL + pgvector               │
│  workspaces · companies · signals · outcomes ·     │
│  signal_weights · intelligence_feed_items · jobs   │
└──────┬─────────────┬──────────────┬────────────────┘
       │             │              │
┌──────▼──────┐ ┌───▼────────┐ ┌──▼──────────────┐
│  Scoring    │ │Intelligence│ │  Model Trainer   │
│  Engine     │ │  Engine    │ │  (weekly)        │
│ ICP match   │ │ GPT-4o     │ │  outcome→weights │
│ decay math  │ │ summaries  │ │                  │
└──────┬──────┘ └───┬────────┘ └──────────────────┘
       └────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              FastAPI Modular Monolith               │
│  /feed · /companies · /signals · /outcomes         │
│  /icp · /auth · /integrations/hubspot              │
└────────────────────┬────────────────────────────────┘
                     │
              Next.js Dashboard (Phase 4.3)
```

**Design decisions:**
- **Modular monolith, not microservices** — one codebase, one deploy, clean module boundaries for future extraction
- **Postgres does almost everything** — JSONB for signals, pgvector for embeddings, no separate vector DB
- **Batch every 6h, not real-time** — buying signals don't need millisecond processing; simpler and more reliable
- **Rule-based scoring first** — ships immediately, replaced by ML as outcome data accumulates (20+ outcomes threshold)

---

## Quick Start (15 minutes)

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- An OpenAI API key (required for intelligence generation)
- An Apollo.io API key (required for lead ingestion; optional for demo)

### 1. Clone and configure

```bash
git clone <repo>
cd avenor
cp .env.example .env
# Edit .env and add your API keys (see Environment Variables below)
```

### 2. Start infrastructure

```bash
docker-compose up postgres redis -d
# Wait for Postgres to be healthy (~10 seconds)
docker-compose ps
```

### 3. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
alembic upgrade head
# Expected: "Running upgrade  -> 001_initial_schema, Initial schema"
```

### 5. Seed demo data

```bash
python scripts/seed.py
# Creates: demo workspace, ICP config, 5 companies, signals, 30 outcomes
# Runs: scoring → model training → feed generation
# Prints: login credentials and test commands
```

### 6. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** — interactive API explorer with all 24 endpoints.

### 7. Login and view your first feed

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@avenor.ai","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# View Account Intelligence Feed
curl -s http://localhost:8000/api/v1/feed \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Pipeline stats
curl -s http://localhost:8000/api/v1/companies/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Model accuracy
curl -s http://localhost:8000/api/v1/outcomes/model-accuracy \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Full Docker Setup

Run everything (API + workers + database) in Docker:

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Check all services are healthy
docker-compose ps

# Run migrations inside the API container
docker-compose exec api alembic upgrade head

# Seed demo data
docker-compose exec api python scripts/seed.py

# View logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f beat

# Stop everything
docker-compose down

# Stop and remove data volumes (full reset)
docker-compose down -v
```

**Services started by docker-compose:**

| Service | Purpose | Port |
|---|---|---|
| `postgres` | Primary database (pgvector) | 5432 |
| `redis` | Task queue broker | 6379 |
| `api` | FastAPI application | 8000 |
| `worker` | Celery task worker | — |
| `beat` | Celery beat scheduler | — |

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Postgres connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `OPENAI_API_KEY` | ✅ | GPT-4o for intelligence generation |
| `APOLLO_API_KEY` | For ingestion | Apollo.io for company/contact data |
| `HUBSPOT_APP_CLIENT_ID` | For HubSpot | OAuth app client ID |
| `HUBSPOT_APP_CLIENT_SECRET` | For HubSpot | OAuth app client secret |
| `HUBSPOT_WEBHOOK_SECRET` | For HubSpot | Webhook signature verification |
| `SERPAPI_KEY` | Optional | Google News for news signals |
| `SLACK_WEBHOOK_URL` | Optional | Reply alert notifications |
| `APP_SECRET_KEY` | ✅ | JWT signing key (generate random 64-char string) |
| `APP_ENV` | ✅ | `development` or `production` |
| `ICP_MIN_EMPLOYEES` | Optional | Default: 50 |
| `ICP_MAX_EMPLOYEES` | Optional | Default: 500 |
| `LLM_CACHE_TTL_HOURS` | Optional | Default: 24 |

**Getting API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Apollo.io: https://app.apollo.io/#/settings/integrations/api
- SerpAPI: https://serpapi.com/dashboard
- Slack webhook: https://api.slack.com/messaging/webhooks

---

## Database Migrations

Avenor uses Alembic for schema migrations.

```bash
# Apply all pending migrations (run this on first setup and after upgrades)
alembic upgrade head

# Check current migration state
alembic current

# See migration history
alembic history

# Create a new migration after model changes
alembic revision --autogenerate -m "add new column"

# Rollback one migration
alembic downgrade -1

# Rollback to empty database
alembic downgrade base
```

---

## Seed Script

`scripts/seed.py` creates realistic demo data without requiring any external API keys.

```bash
# Initial seed
python scripts/seed.py

# Reset and re-seed (clears previous demo data)
python scripts/seed.py --reset
```

**What it creates:**
- 1 workspace (`Avenor Demo`) with full ICP configuration
- 1 admin user: `demo@avenor.ai` / `demo1234`
- 5 companies with signals (Veridian Labs, Meridian Health Tech, Apex Revenue Co, NovaBuild Systems, TinyMart)
- Contacts for each company
- 30 historical outcomes for model training
- Runs scoring → model recalibration → feed generation

**After seeding, Veridian Labs and Meridian Health Tech score above the active threshold** (HOT/WARM buying windows) while TinyMart (wrong industry/size) scores low — demonstrating ICP filtering works correctly.

---

## API Documentation

Interactive docs: **http://localhost:8000/docs**

### Authentication

All endpoints (except `/health`) require a JWT Bearer token.

```bash
# Register new workspace
POST /api/v1/auth/register
{"email": "you@company.com", "password": "...", "full_name": "...", "workspace_name": "..."}

# Login
POST /api/v1/auth/login
{"email": "you@company.com", "password": "..."}
→ {"access_token": "...", "workspace_id": "..."}

# Use token
Authorization: Bearer <access_token>
```

### Core endpoints

```bash
# Configure your ICP
PUT /api/v1/icp
{"industries": ["SaaS"], "min_employees": 50, "max_employees": 500, ...}

# Get Account Intelligence Feed (ordered by score)
GET /api/v1/feed
GET /api/v1/feed?buying_window=hot&min_score=0.6

# Get intelligence for specific company
GET /api/v1/feed/company/{company_id}

# Refresh feed on-demand
POST /api/v1/feed/refresh

# List companies
GET /api/v1/companies?status=active&buying_window=hot
GET /api/v1/companies/stats

# View signals
GET /api/v1/signals?company_id={id}
POST /api/v1/signals   # add manual signal

# Log outcome (trains the model)
POST /api/v1/outcomes
{"company_id": "...", "outcome_type": "meeting_booked", "notes": "..."}

# View model accuracy
GET /api/v1/outcomes/model-accuracy

# Trigger pipeline manually
POST /api/v1/admin/pipeline/trigger

# HubSpot
GET /api/v1/integrations/hubspot/connect     # get OAuth URL
GET /api/v1/integrations/hubspot/status
POST /api/v1/integrations/hubspot/webhook    # webhook receiver
```

### Outcome types

| Value | Description |
|---|---|
| `became_opportunity` | Account entered active sales process |
| `meeting_booked` | Meeting scheduled |
| `replied_positive` | Positive reply to outreach |
| `replied_negative` | Negative reply |
| `no_response` | No response after outreach |
| `wrong_timing` | Not ready to buy |
| `closed_won` | Deal closed (auto-captured from HubSpot) |
| `closed_lost` | Deal lost (auto-captured from HubSpot) |

---

## Testing

```bash
# Unit tests (no database required — run anywhere)
python -m pytest tests/unit/ -v

# All tests (integration tests skip without Postgres)
python -m pytest tests/ -v

# Integration tests with real Postgres
TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db \
  python -m pytest tests/integration/ -v

# With coverage
python -m pytest tests/unit/ --cov=app/modules/scoring --cov-report=term-missing
```

**Test coverage priorities:**
- `app/modules/scoring/engine.py` — 20 unit tests covering all scoring logic
- `tests/integration/` — 9 end-to-end tests (require Postgres) covering ingestion → scoring → feed → outcome loop

---

## Background Workers

Workers run as separate Celery processes. The beat scheduler triggers jobs on cron schedules.

```bash
# Start worker (handles signal, scoring, intelligence, training queues)
celery -A app.workers.celery_app worker --loglevel=info \
  --queues=signals,scoring,intelligence,training,pipeline

# Start beat scheduler (triggers jobs on schedule)
celery -A app.workers.celery_app beat --loglevel=info

# Trigger a full pipeline run manually (useful for testing)
python -c "
from app.workers.tasks import run_full_pipeline_for_workspace
run_full_pipeline_for_workspace.delay('<workspace_id>')
"
```

**Job schedule:**

| Job | Schedule | What it does |
|---|---|---|
| Signal collection | Every 6 hours | Apollo + News for all workspaces |
| Scoring | 30 min after collection | Recompute all company scores |
| Feed generation | Daily at 2am UTC | Generate/refresh intelligence items |
| Model recalibration | Weekly Saturday 2am | Update signal weights from outcomes |

**Monitoring jobs:** `GET /admin/status` returns the last 10 jobs with status, duration, and any errors.

---

## Module Guide

| Module | File | Purpose |
|---|---|---|
| Config | `app/core/config.py` | Typed settings from environment |
| Exceptions | `app/core/exceptions.py` | Domain exception hierarchy |
| Signal config | `app/core/signal_config.py` | Weight priors, decay half-lives, ICP multipliers |
| Database | `app/db/session.py` | Engine, session factory, `init_db()` |
| Models | `app/models/__init__.py` | All 13 SQLAlchemy table models |
| Apollo collector | `app/modules/signals/apollo_collector.py` | Fetch companies+contacts from Apollo |
| News collector | `app/modules/signals/news_collector.py` | Monitor company news via SerpAPI |
| Scoring engine | `app/modules/scoring/engine.py` | ICP match, decay, composite score, buying window |
| Model trainer | `app/modules/scoring/trainer.py` | Recalibrate weights from outcome data |
| Intelligence engine | `app/modules/intelligence/engine.py` | GPT-4o summaries, angle recommendations, feed items |
| Celery app | `app/workers/celery_app.py` | Task queue config and beat schedule |
| Tasks | `app/workers/tasks.py` | All Celery task definitions with job audit |
| Auth | `app/api/auth.py` | JWT creation/validation, workspace scoping |
| HubSpot | `app/integrations/hubspot/routes.py` | OAuth flow, webhook receiver, outcome capture |

---

## Known Limitations

**Scoring accuracy on day one:** With 0 customer outcome data, signal weights are expert priors (Forrester/TOPO research). The model becomes genuinely predictive after ~20 logged outcomes. The system is honest about this — `GET /api/v1/outcomes/model-accuracy` shows how many outcomes have been logged and current accuracy.

**Apollo API rate limits:** Apollo's free tier allows 50 requests/month. Growth plans allow 10,000. The ingestion pipeline respects rate limits via exponential backoff (tenacity) and processes workspaces sequentially.

**pgvector similarity search:** Company embeddings are only generated when `OPENAI_API_KEY` is set. Without embeddings, the "similar converted companies" feature falls back to industry+size matching, which is less accurate.

**Token encryption:** The HubSpot token encryption in MVP uses a simple XOR cipher for speed of implementation. Before handling real customer OAuth tokens in production, replace `_encrypt`/`_decrypt` in `app/integrations/hubspot/routes.py` with Python's `cryptography.fernet.Fernet`.

**No LinkedIn integration:** LinkedIn automation is excluded from Phase 4.1. The outreach module (`app/modules/outreach/`) is a stub — the automation layer built in Phase 0 (Nexus) can be ported here in Phase 4.2.

**SQLite not supported:** The application uses Postgres-specific types (JSONB, pgvector, UUID). SQLite cannot be used as a drop-in replacement. Use the provided docker-compose for local development.

**Celery broker:** Uses Redis. For very high job volume (>10,000 tasks/hour), consider migrating to RabbitMQ. Not needed until you have >500 active workspaces.

---

## What's Next (Phase 4.2 and 4.3)

**Phase 4.2 — HubSpot integration completion:**
- Historical deal sync (90-day backfill on connection)
- Salesforce integration
- Two-way CRM sync (push Avenor scores into CRM as custom properties)

**Phase 4.3 — Customer Dashboard:**
- Next.js frontend consuming these APIs
- Account Intelligence Feed UI
- Outcome logging workflow
- Pipeline analytics view
- ICP configuration wizard

**Later:**
- LinkedIn signal monitoring
- XGBoost ML model replacing rule-based scorer (at 500+ outcomes)
- Multi-workspace admin panel
- Stripe billing integration
- SOC 2 compliance preparation

---

## Development Tips

```bash
# Watch logs in real time
uvicorn app.main:app --reload --log-level debug

# Reset database completely
alembic downgrade base && alembic upgrade head && python scripts/seed.py --reset

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Check what Alembic would generate (dry run)
alembic revision --autogenerate -m "test" --sql

# Run a specific scoring recalibration manually
python -c "
from app.db.session import db_session
from app.modules.scoring.trainer import recalibrate_weights
with db_session() as db:
    result = recalibrate_weights(db, 'YOUR_WORKSPACE_ID')
    print(result)
"
```
