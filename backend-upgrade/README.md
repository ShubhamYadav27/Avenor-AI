# Avenor — Predictive Revenue Intelligence

> Know who is about to buy, why, and what to say — before any competitor does.

Avenor is a self-improving B2B revenue intelligence platform. It monitors companies
for buying signals, scores them against your ICP, surfaces an Account Intelligence
Feed, connects to your CRM, and learns from every win and loss to improve predictions.

**Current version:** v0.2-crm (Phase 4.2 complete)

---

## What This System Does

### Phase 4.1 — Intelligence Backend
1. **Ingests signals** — hiring, funding, tech changes, leadership changes, news
2. **Scores accounts** — composite signal scoring with ICP matching and recency decay
3. **Predicts buying windows** — HOT (0–30d), WARM (30–60d), WATCH (60–90d), COLD
4. **Generates intelligence** — GPT-4o signal summaries and recommended outreach angles
5. **Logs outcomes** — win/loss feedback feeds the prediction model

### Phase 4.2 — CRM Intelligence & Feedback Loop
6. **HubSpot integration** — OAuth2, full CRM sync, historical deal import
7. **Outcome attribution** — every closed deal linked back to original signals and recommendations
8. **Signal effectiveness** — answers "which signals actually predict revenue?"
9. **Prediction accuracy** — measures Avenor's forecast precision over time
10. **Self-improvement** — weekly recalibration uses outcome data to update signal weights

The core moat: **Signals → Predictions → CRM Outcomes → Learning → Better Predictions**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                External Data Sources                        │
│  Apollo · Crunchbase · BuiltWith · News · HubSpot CRM      │
└──────────────────────┬──────────────────────────────────────┘
                       │ batch every 6h / HubSpot every 30min
┌──────────────────────▼──────────────────────────────────────┐
│              Signal + CRM Ingestion Workers                 │
│    apollo_collector · news_collector · hubspot sync         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              PostgreSQL 16 + pgvector                       │
│  13 Phase 4.1 tables + 5 Phase 4.2 tables = 18 total      │
│  workspaces · companies · signals · outcomes ·              │
│  hubspot_deals · outcome_attributions · signal_effectiveness│
└──────┬──────────────┬────────────────┬───────────────────────┘
       │              │                │
┌──────▼─────┐ ┌──────▼──────┐ ┌──────▼──────────────────────┐
│  Scoring   │ │Intelligence │ │  CRM Intelligence            │
│  Engine    │ │  Engine     │ │  attribution · feedback loop │
│ ICP+decay  │ │ GPT-4o      │ │  signal effectiveness        │
│ combo bonus│ │ summaries   │ │  prediction accuracy         │
└──────┬─────┘ └──────┬──────┘ └─────────────────────────────┘
       └──────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Modular Monolith (32 endpoints)        │
│  /feed · /companies · /signals · /outcomes · /icp · /auth  │
│  /intelligence · /integrations/hubspot                      │
└─────────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- Modular monolith — one deploy, one codebase, clean module boundaries
- Postgres handles everything at this scale (JSONB, pgvector, no separate vector DB)
- Batch processing every 6h for signals, 30min for CRM sync
- Rule-based scoring on day one, replaced by learned weights after 20+ outcomes
- Fernet (AES-128-CBC + HMAC-SHA256) for all CRM token storage

---

## Quick Start (15 minutes)

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- OpenAI API key (for intelligence generation)
- Apollo.io API key (for lead ingestion; demo works without it)

### 1. Clone and configure

```bash
git clone <repo>
cd avenor
cp .env.example .env
```

Edit `.env` — minimum required:
```bash
OPENAI_API_KEY=sk-...
APP_SECRET_KEY=<random 64-char string>
# Generate an encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste result into:
ENCRYPTION_KEY=<paste here>
```

### 2. Start infrastructure

```bash
docker-compose up postgres redis -d
# Wait ~10 seconds for postgres health check
docker-compose ps
```

### 3. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
# Apply all migrations (Phase 4.1 + Phase 4.2)
alembic upgrade head

# Verify: should show 18 tables
python -c "import app.models; print(sorted(app.models.Base.metadata.tables.keys()))"
```

### 5. Seed demo data

```bash
python scripts/seed.py
# Creates: workspace, ICP config, 5 companies, signals, 30 outcomes
# Prints: login credentials and curl commands
```

### 6. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** — 32 endpoints, all documented.

### 7. Quick test

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@avenor.ai","password":"demo1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Account Intelligence Feed
curl -s http://localhost:8000/api/v1/feed \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Signal effectiveness (after seeding)
curl -s http://localhost:8000/api/v1/intelligence/signal-effectiveness \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Prediction accuracy
curl -s http://localhost:8000/api/v1/intelligence/accuracy \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Full Docker Setup

```bash
# Configure environment
cp .env.example .env
# Edit .env with your keys

# Start all services
docker-compose up -d

# Run migrations inside API container
docker-compose exec api alembic upgrade head

# Seed demo data
docker-compose exec api python scripts/seed.py

# View logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f beat

# Reset everything
docker-compose down -v && docker-compose up -d
```

**Services:**

| Service | Purpose | Port |
|---|---|---|
| `postgres` | Primary database (pgvector/pg16) | 5432 |
| `redis` | Celery broker | 6379 |
| `api` | FastAPI application | 8000 |
| `worker` | Celery task worker | — |
| `beat` | Celery beat scheduler | — |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | ✅ | `redis://host:6379/0` |
| `APP_SECRET_KEY` | ✅ | JWT signing key (random 64-char string) |
| `OPENAI_API_KEY` | ✅ | GPT-4o for intelligence generation |
| `ENCRYPTION_KEY` | ✅ prod | Fernet key for CRM token storage |
| `APOLLO_API_KEY` | For ingestion | Apollo.io company/contact data |
| `HUBSPOT_APP_CLIENT_ID` | For HubSpot | OAuth app client ID |
| `HUBSPOT_APP_CLIENT_SECRET` | For HubSpot | OAuth app client secret |
| `HUBSPOT_WEBHOOK_SECRET` | For HubSpot | Webhook signature verification |
| `SERPAPI_KEY` | Optional | Google News for news signals |
| `SLACK_WEBHOOK_URL` | Optional | Reply alert notifications |
| `HUBSPOT_HISTORICAL_DAYS` | Optional | Days of history to import (default: 180) |
| `HUBSPOT_SYNC_INTERVAL_MINUTES` | Optional | CRM sync frequency (default: 30) |
| `SENTRY_DSN` | Optional | Error tracking |

**Generating keys:**
```bash
# APP_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY (Fernet — required for HubSpot in production)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## HubSpot Setup Guide

### 1. Create a HubSpot Private App

1. In HubSpot: Settings → Integrations → Private Apps → Create private app
2. Scopes required:
   - `crm.objects.deals.read`
   - `crm.objects.companies.read`
   - `crm.objects.contacts.read`
   - `crm.objects.owners.read`
3. Note the **Client ID** and **Client Secret**

### 2. Configure Avenor

```bash
HUBSPOT_APP_CLIENT_ID=<your client id>
HUBSPOT_APP_CLIENT_SECRET=<your client secret>
HUBSPOT_WEBHOOK_SECRET=<random string you choose>
ENCRYPTION_KEY=<generated Fernet key>
```

### 3. Connect a workspace

```bash
# Get OAuth URL
curl -s http://localhost:8000/api/v1/integrations/hubspot/connect \
  -H "Authorization: Bearer $TOKEN"
# → Open the auth_url in your browser, authorize, get redirected back

# Check connection status
curl -s http://localhost:8000/api/v1/integrations/hubspot/status \
  -H "Authorization: Bearer $TOKEN"
```

### 4. What happens after connection

On first connect, Avenor automatically:
1. Registers webhook subscriptions (deal stage changes, deal creation)
2. Imports the past 180 days of HubSpot deals (historical import)
3. Matches deals to Avenor companies by domain
4. Creates Outcome records for closed-won and closed-lost deals
5. Runs attribution to link outcomes back to signals and recommendations
6. Computes initial signal effectiveness metrics

### 5. Webhook setup (production)

Your public webhook URL must be registered with HubSpot:
```
https://your-domain.com/api/v1/integrations/hubspot/webhook
```
Avenor auto-registers this via the HubSpot webhooks API on connect.
For local development, use ngrok: `ngrok http 8000`

### 6. Sync schedule

| Event | Trigger | What syncs |
|---|---|---|
| On connect | Immediate | All owners, 180 days of deals |
| Every 30 min | Celery beat | Deals + contacts modified since last run |
| On webhook | Real-time | Deal stage changes → Outcome logging |
| Weekly Saturday | Celery beat | Model recalibration + signal effectiveness |

---

## Database Migrations

```bash
# Apply all migrations from empty database
alembic upgrade head

# Apply only Phase 4.1 (test incremental upgrade)
alembic upgrade 001_initial_schema

# Apply Phase 4.2 on top
alembic upgrade 002_phase42_crm_intelligence

# Check current state
alembic current

# Full migration history
alembic history --verbose

# Roll back Phase 4.2 only (keeps Phase 4.1)
alembic downgrade 001_initial_schema

# Roll back everything
alembic downgrade base
```

**Migration chain:**
```
(empty) → 001_initial_schema (13 tables) → 002_phase42_crm_intelligence (+5 tables = 18 total)
```

---

## API Reference

All endpoints documented interactively at **http://localhost:8000/docs**

### Phase 4.1 Endpoints (24)
- `POST /api/v1/auth/register` — create workspace + admin user
- `POST /api/v1/auth/login` — get JWT token
- `GET  /api/v1/auth/me` — current user info
- `GET/PUT /api/v1/icp` — ICP configuration
- `GET  /api/v1/feed` — Account Intelligence Feed
- `GET  /api/v1/feed/company/{id}` — company detail + signals
- `POST /api/v1/feed/refresh` — on-demand feed refresh
- `POST /api/v1/feed/dismiss` — hide a company from feed
- `GET  /api/v1/companies` — list companies with filters
- `GET  /api/v1/companies/stats` — pipeline health counts
- `GET  /api/v1/companies/{id}/score` — score breakdown
- `POST /api/v1/companies/score` — trigger scoring job
- `GET  /api/v1/signals` — list signals
- `POST /api/v1/signals` — add manual signal
- `GET  /api/v1/signals/types` — valid signal types
- `POST /api/v1/outcomes` — log outcome (trains model)
- `GET  /api/v1/outcomes` — list outcomes
- `GET  /api/v1/outcomes/model-accuracy` — accuracy stats
- `GET  /health` — public health check
- `GET  /admin/status` — system status + job history
- `POST /admin/pipeline/trigger` — manual pipeline run

### Phase 4.2 Endpoints (8 new)
- `GET  /api/v1/integrations/hubspot/connect` — OAuth URL
- `GET  /api/v1/integrations/hubspot/callback` — OAuth callback
- `GET  /api/v1/integrations/hubspot/status` — connection + sync state
- `POST /api/v1/integrations/hubspot/sync/trigger` — manual incremental sync
- `POST /api/v1/integrations/hubspot/sync/historical` — re-run historical import
- `DELETE /api/v1/integrations/hubspot/disconnect` — disconnect HubSpot
- `POST /api/v1/integrations/hubspot/webhook` — webhook receiver
- `GET  /api/v1/intelligence/attribution` — ROI summary
- `GET  /api/v1/intelligence/attribution/deals` — deal-level attribution
- `GET  /api/v1/intelligence/signal-effectiveness` — signal analytics
- `GET  /api/v1/intelligence/accuracy` — prediction accuracy report
- `POST /api/v1/intelligence/feedback-loop/run` — manual feedback loop
- `GET  /api/v1/intelligence/crm/deals` — synced CRM deals

---

## Testing

```bash
# Unit tests (no database required)
python -m pytest tests/unit/ -v

# All tests (integration tests skip without Postgres)
python -m pytest tests/ -v

# Integration tests (requires Postgres)
TEST_DATABASE_URL=postgresql://avenor_user:avenor_pass@localhost/avenor_test \
  python -m pytest tests/integration/ -v

# With coverage
python -m pytest tests/unit/ --cov=app --cov-report=term-missing
```

**Test count:** 55 unit tests, 9 integration tests (Postgres-gated)

**Coverage by module:**
- `app/modules/scoring/engine.py` — 20 tests (ICP match, decay, combinations, full score)
- `app/utils/encryption.py` — 12 tests (round-trip, key management, migration)
- `app/integrations/hubspot/` — 14 tests (tokens, sync helpers, webhooks, attribution)
- `app/modules/outcomes/` — 9 tests (attribution logic, feedback loop, accuracy report)

---

## Background Workers

```bash
# Start worker (handles all queues)
celery -A app.workers.celery_app worker --loglevel=info \
  --queues=signals,scoring,intelligence,training,pipeline

# Start beat scheduler
celery -A app.workers.celery_app beat --loglevel=info
```

**Scheduled jobs:**

| Job | Schedule | What it does |
|---|---|---|
| Signal collection | Every 6h | Apollo + News for all workspaces |
| Scoring | 6h + 30min | Recompute all scores |
| Feed generation | Daily 2am UTC | Generate intelligence items |
| HubSpot sync | Every 30min | Incremental CRM sync |
| Model recalibration | Saturday 2am | Update signal weights from outcomes |
| Signal effectiveness | Saturday 2:30am | Recompute which signals predict revenue |

---

## Module Guide

| Module | File | Purpose |
|---|---|---|
| Config | `app/core/config.py` | Typed settings, all env vars |
| Encryption | `app/utils/encryption.py` | Fernet token encryption/decryption |
| Models | `app/models/__init__.py` | All 18 SQLAlchemy table models |
| Scoring | `app/modules/scoring/engine.py` | ICP match, decay, composite score |
| Trainer | `app/modules/scoring/trainer.py` | Weekly weight recalibration |
| Intelligence | `app/modules/intelligence/engine.py` | GPT-4o summaries + angle generation |
| Attribution | `app/modules/outcomes/attribution.py` | Link outcomes → signals → feed items |
| Feedback loop | `app/modules/outcomes/feedback_loop.py` | Signal effectiveness + accuracy metrics |
| HubSpot client | `app/integrations/hubspot/client.py` | Authenticated API wrapper, pagination |
| HubSpot sync | `app/integrations/hubspot/sync.py` | Company/contact/deal sync + historical import |
| HubSpot routes | `app/integrations/hubspot/routes.py` | OAuth, webhook, sync endpoints |
| CRM intelligence | `app/api/routes/intelligence.py` | Attribution + effectiveness API |
| Workers | `app/workers/tasks.py` | All Celery tasks + job audit |

---

## Known Limitations

**Encryption key rotation:** There is no automated key rotation. If you change `ENCRYPTION_KEY`,
existing encrypted tokens in `hubspot_connections` become unreadable. Migration path:
decrypt all tokens with the old key, re-encrypt with the new key before rotating.

**HubSpot deal matching:** Company matching uses domain → HubSpot ID → fuzzy name (>85% similarity).
Companies with no domain and unusual names may create stub records instead of matching
existing Avenor companies. Review the `crm_stub_company_created` log events after first sync.

**Historical import volume:** The 180-day historical import can be slow for large HubSpot
portals (thousands of deals). The `HUBSPOT_HISTORICAL_BATCH_SIZE=100` setting controls
commit frequency. For portals with >10,000 deals, increase this or reduce `HUBSPOT_HISTORICAL_DAYS`.

**Token encryption migration:** Existing Phase 4.1 deployments with XOR-encrypted tokens
in `hubspot_connections` are automatically migrated to Fernet on first token use (the
`migrate_legacy_token` function handles this transparently).

**Signal effectiveness minimum:** Signal effectiveness metrics require at least 5 outcomes
per signal type before computing. Early-stage workspaces (< 20 total outcomes) will see
"no data" responses from `/intelligence/signal-effectiveness`.

**No Salesforce integration:** Phase 4.2 delivers HubSpot only. Salesforce is Phase 4.3+.

---

## What Remains for Phase 4.3

**Customer Dashboard (Next.js)**
- Account Intelligence Feed UI with filtering and sorting
- Company detail view with signal timeline
- Outcome logging workflow (inline from feed)
- Pipeline analytics: attribution ROI, signal effectiveness charts
- ICP configuration wizard
- HubSpot connection setup flow

**Additional integrations**
- Salesforce OAuth + sync (mirrors HubSpot implementation)
- Slack notifications for hot accounts
- Calendly integration for meeting booking

**Model improvements**
- XGBoost ML model replacing rule-based scorer (at 500+ outcomes)
- Automated weight application from `get_scoring_recommendations()`
- Cross-workspace anonymized signal effectiveness (aggregate moat)

**Operational**
- Stripe billing integration
- SOC 2 compliance preparation
- Multi-region Postgres setup

---

## Development Reference

```bash
# Reset database completely
alembic downgrade base && alembic upgrade head && python scripts/seed.py --reset

# Generate migration after model changes
alembic revision --autogenerate -m "describe change"

# Run attribution manually for a workspace
python -c "
from app.db.session import db_session
from app.modules.outcomes.attribution import run_attribution_for_workspace
with db_session() as db:
    result = run_attribution_for_workspace(db, 'WORKSPACE_ID')
    print(result)
"

# Run signal effectiveness computation
python -c "
from app.db.session import db_session
from app.modules.outcomes.feedback_loop import run_full_feedback_loop
with db_session() as db:
    result = run_full_feedback_loop(db, 'WORKSPACE_ID')
    print(result)
"

# Test HubSpot connection status
curl -s http://localhost:8000/api/v1/integrations/hubspot/status \
  -H "Authorization: Bearer \$TOKEN" | python3 -m json.tool
```
