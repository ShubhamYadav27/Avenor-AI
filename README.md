# Nexus — Adaptive AI Outbound System

MVP backend: signals → scoring → personalized outreach → reply learning.

---

## Quick Start (15 minutes)

### 1. Clone and install

```bash
git clone <your-repo>
cd nexus
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the database

```bash
docker-compose up -d
# Postgres running on localhost:5432
# Redis running on localhost:6379
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys (see section below)
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for the interactive API explorer.

### 5. Test without any API keys

```bash
python scripts/test_pipeline.py
```

This seeds mock data, runs scoring, and validates the full pipeline
without hitting Apollo or OpenAI.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Postgres connection string |
| `OPENAI_API_KEY` | Yes (for generation) | GPT-4o access |
| `APOLLO_API_KEY` | Yes (for fetch) | Apollo.io API key |
| `INSTANTLY_API_KEY` | No | Instantly.ai (leave blank → mock sender) |
| `INSTANTLY_CAMPAIGN_ID` | No | Your Instantly campaign ID |
| `SLACK_WEBHOOK_URL` | No | Slack incoming webhook for reply alerts |
| `ICP_INDUSTRIES` | No | Comma-separated industries (default: SaaS,FinTech,B2B Software) |
| `ICP_MIN_EMPLOYEES` | No | Min company size (default: 50) |
| `ICP_MAX_EMPLOYEES` | No | Max company size (default: 500) |
| `ICP_LOCATIONS` | No | Comma-separated locations (default: United States,...) |

### Where to get API keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Apollo.io**: https://app.apollo.io/#/settings/integrations/api
- **Instantly**: https://app.instantly.ai/app/settings/integrations
- **Slack webhook**: https://api.slack.com/messaging/webhooks

---

## API Reference

### Run the full pipeline (recommended first call)

```bash
# Dry run (safe — stages everything, sends nothing)
curl -X POST http://localhost:8000/api/v1/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "fetch_limit": 10,
    "max_leads_to_contact": 5,
    "sender_name": "Alex",
    "sender_company": "YourCompany",
    "product_description": "a data pipeline tool for fast-growing engineering teams",
    "dry_run": true
  }'

# Live run — actually sends
curl -X POST http://localhost:8000/api/v1/run-pipeline \
  -d '{"dry_run": false, "max_leads_to_contact": 5}'
```

### Step by step

```bash
# 1. Fetch leads from Apollo
curl -X POST http://localhost:8000/api/v1/ingest-leads \
  -H "Content-Type: application/json" \
  -d '{
    "industries": ["SaaS", "FinTech"],
    "min_employees": 50,
    "max_employees": 300,
    "limit": 25
  }'

# 2. Score all unscored leads
curl -X POST http://localhost:8000/api/v1/score-leads \
  -H "Content-Type: application/json" \
  -d '{}'

# 3. View top leads
curl "http://localhost:8000/api/v1/leads?status=queued&limit=10"

# 4. Generate a message for a specific lead
curl -X POST http://localhost:8000/api/v1/generate-message \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "<uuid-from-leads-response>",
    "contact_id": "<uuid-from-contacts>",
    "sender_name": "Alex",
    "product_description": "a data pipeline tool",
    "angle": "pain_led"
  }'

# 5. Send a message (dry_run=false for real send)
curl -X POST http://localhost:8000/api/v1/send-outreach \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "<uuid-from-generate>",
    "from_name": "Alex",
    "dry_run": true
  }'

# 6. Handle an incoming reply
curl -X POST http://localhost:8000/api/v1/handle-reply \
  -H "Content-Type: application/json" \
  -d '{
    "outreach_message_id": "<uuid>",
    "reply_text": "Yes, this is great timing. Can we hop on a call this week?"
  }'

# 7. Check pipeline status
curl http://localhost:8000/api/v1/status
```

---

## Project Structure

```
nexus/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, middleware
│   ├── config.py                # Settings from env vars
│   ├── api/
│   │   └── routes.py            # All API endpoints
│   ├── core/
│   │   └── pipeline.py          # run_pipeline() orchestrator
│   ├── db/
│   │   └── session.py           # DB engine, session, init_db()
│   ├── models/
│   │   └── __init__.py          # All SQLAlchemy models
│   └── services/
│       ├── apollo_fetcher.py    # Apollo API integration
│       ├── scoring_engine.py    # ICP match + signal scoring
│       ├── message_generator.py # GPT-4o personalization
│       ├── outreach_sender.py   # Instantly + mock sender
│       └── reply_classifier.py  # Reply intent classification
├── scripts/
│   └── test_pipeline.py         # End-to-end test with mock data
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## Scoring Logic

Composite score = `Σ(signal_decayed) × ICP_multiplier`

| Signal | Base weight | Half-life |
|---|---|---|
| Funding round | 0.35 | 90 days |
| Key hire | 0.25 | 30 days |
| Tech change | 0.20 | 60 days |
| Intent surge | 0.15 | 14 days |
| Expansion | 0.05 | 45 days |

| ICP match | Multiplier |
|---|---|
| All 3 criteria (industry + size + location) | 1.5× |
| 2 of 3 criteria | 1.0× |
| 1 or fewer criteria | 0.3× |

Thresholds: ≥ 0.60 → active outreach queue · 0.30–0.59 → nurture · < 0.30 → disqualified

---

## Message Quality Gate

Every generated message must pass before sending:

- Word count: 20–80 words
- No banned phrases (e.g. "hope this finds you well")
- Does not start with "I"
- Subject: 3–60 characters
- Subject present and non-empty

Failed messages are stored as drafts with `passed_quality_gate=false`
and `quality_gate_notes` explaining what failed. They are never sent automatically.

---

## What to build next (post-MVP)

1. **Hiring signal monitor** — poll LinkedIn Jobs / Adzuna daily, push to signals table
2. **Multi-step sequences** — auto-schedule touch 2–5 based on reply/open status
3. **LinkedIn outreach** — Heyreach API integration
4. **Feedback ML model** — XGBoost on signal+outcome data to replace rule-based scoring
5. **RAG message improvement** — retrieve top-performing past messages as few-shot examples
6. **Dashboard** — Next.js frontend consuming these APIs
7. **CRM sync** — direct HubSpot/Salesforce API (replace Zapier)
