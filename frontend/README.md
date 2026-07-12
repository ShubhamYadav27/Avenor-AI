# Avenor Dashboard — Customer Intelligence Frontend

Next.js 16 frontend for the Avenor Predictive Revenue Intelligence platform.
Connects to the Phase 4.1/4.2 FastAPI backend.

## Tech stack
- **Next.js 16** App Router · TypeScript · Tailwind CSS v4
- **React Query v5** for server state
- **Axios** for HTTP with auto auth headers
- **Recharts** for analytics charts
- **Radix UI** primitives for accessible components
- **Lucide React** for icons

## Quick start

```bash
# 1. Install
npm install

# 2. Configure
cp .env.local.example .env.local
# Edit .env.local: set NEXT_PUBLIC_API_URL to your backend URL

# 3. Run (backend must be running first)
npm run dev
# Open http://localhost:3000

# Demo login (after running backend seed.py):
# Email: demo@avenor.ai
# Password: demo1234
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

## Pages

| Route | Description |
|---|---|
| `/login` | Sign in with email + password |
| `/register` | Create new workspace |
| `/dashboard/feed` | **Main screen** — Account Intelligence Feed |
| `/dashboard/companies` | All monitored companies with filters |
| `/dashboard/companies/[id]` | Company detail: signals, contacts, AI recommendations |
| `/dashboard/analytics` | Signal effectiveness, prediction accuracy, win/loss charts |
| `/dashboard/hubspot` | HubSpot CRM connection and sync status |
| `/dashboard/settings` | Workspace info, model status, pipeline controls |

## Backend connection

The frontend requires the Avenor backend (Phase 4.1 + 4.2) running at `NEXT_PUBLIC_API_URL`.

```bash
# Start backend (from avenor/ directory)
docker-compose up postgres redis -d
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

All API calls use the JWT token stored in cookies (`avenor_token`).
Token expiry redirects to `/login` automatically.

## Build

```bash
npm run build   # production build
npm run lint    # ESLint
npm run dev     # development server
```

## Project structure

```
avenor-dashboard/
├── app/                    # Next.js App Router pages
│   ├── dashboard/          # Protected dashboard routes
│   │   ├── feed/           # Intelligence Feed (main screen)
│   │   ├── companies/      # Companies list + detail
│   │   ├── analytics/      # Signal effectiveness & accuracy
│   │   ├── hubspot/        # CRM integration
│   │   └── settings/       # Workspace & model settings
│   ├── login/              # Auth pages
│   └── register/
├── components/
│   ├── feed/               # Feed card component
│   ├── layout/             # Sidebar, TopBar, AuthGuard
│   ├── outcomes/           # Outcome logging modal
│   └── ui/                 # Reusable primitives
├── hooks/
│   └── use-api.ts          # All React Query hooks
├── lib/
│   ├── api-client.ts       # Axios instance + error handling
│   ├── auth.ts             # Token management (cookies)
│   └── utils.ts            # Formatters, constants
└── types/
    └── api.ts              # TypeScript types matching backend contracts
```
