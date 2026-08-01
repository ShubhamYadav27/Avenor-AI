import os
import zipfile

ROOT_DIR = r"c:\Avenor\backend-upgrade"
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

os.makedirs(DOCS_DIR, exist_ok=True)

# ---------------------------------------------------------
# ROOT FILES
# ---------------------------------------------------------

README = """<div align="center">
  <img src="https://via.placeholder.com/150x150/000000/FFFFFF?text=AVENOR" alt="AVENOR-AI Logo" width="120" />
  <h1>AVENOR-AI</h1>
  <h3>AI-Native Predictive Revenue Intelligence Platform</h3>
  <p>Become the world's AI operating system for B2B Revenue Intelligence.</p>
</div>

---

## 📖 Project Overview
AVENOR-AI is a hyperscale, enterprise-grade Revenue Intelligence Platform. It replaces legacy CRMs (like Salesforce) and static data providers (like ZoomInfo) with a unified, autonomous **Intelligence Cloud**. By natively integrating a vector-based Knowledge Graph with Foundation Revenue Models, AVENOR-AI empowers Go-To-Market teams to operate with autonomous precision.

## 🎯 Mission
Help revenue teams know exactly **WHO** to contact, **WHEN** to contact them, **WHY** they are likely to buy, and **WHAT** actions should be taken next using explainable AI.

## 🔭 Vision
Become the world's AI operating system for B2B Revenue Intelligence—a true Cognitive Digital Twin of the enterprise revenue engine.

---

## ⚡ Platform Highlights

- **AI-Native Architecture**: Built from the ground up on a vector-native Knowledge Graph, discarding legacy relational constraints.
- **Enterprise Intelligence**: 12 proprietary intelligence engines actively crawling and resolving global signals (Funding, Hiring, Intent).
- **Autonomous Agents**: Instead of providing static lists, AVENOR's Agents autonomously research buying committees and draft personalized outreach.
- **Constitutional AI Safety**: Every AI decision is mathematically evaluated against strict Hallucination Detection constraints and Human-In-The-Loop approval queues.

---

## 🛠️ Technology Stack
- **Frontend**: React, Next.js, TailwindCSS (Glass-card UI)
- **Backend Edge**: Python, FastAPI, Celery
- **Data Persistence**: PostgreSQL, Redis, Vector Database
- **AI/ML Layer**: PyTorch, HuggingFace, Enterprise Feature Store
- **Infrastructure**: Kubernetes, Terraform, Multi-Region Active-Passive Routing

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    UI[Revenue OS UI] --> Gateway[FastAPI Edge Gateway]
    Gateway --> Application[Clean Architecture Modules]
    Application --> PG[(PostgreSQL)]
    Application --> Agents[Autonomous Agent Platform]
    Agents --> FeatureStore[Feature Store]
    Agents --> Governance[AI Governance Engine]
    FeatureStore --> Vector[(Knowledge Graph Vector DB)]
```

*For a deep dive, read our [Architecture Guide](docs/ARCHITECTURE.md).*

---

## 🚀 Quick Start & Installation

To spin up the local development environment:

```bash
git clone git@github.com:Avenor/Avenor-AI.git
cd Avenor-AI
cp .env.example .env

# Start Persistence Layer (PostgreSQL, Redis, Vector DB)
docker-compose up -d

# Start API Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Start Frontend
cd frontend
npm install
npm run dev
```
*See the [Developer Guide](docs/DEVELOPER_GUIDE.md) for full instructions.*

---

## 📂 Repository & Documentation Structure

The definitive documentation suite is located in the `docs/` directory.

| Documentation | Description |
|--------------|-------------|
| 📐 [**Architecture**](docs/ARCHITECTURE.md) | High-level system design, Data Flow, Tech Stack. |
| 🧩 [**Modules**](docs/MODULES.md) | Core components: Revenue OS, Copilot, Marketplace. |
| 🗺️ [**Roadmap**](docs/ROADMAP.md) | The 10-phase engineering roadmap and future vision. |
| 🗄️ [**Database**](docs/DATABASE.md) | ER Diagrams, Partitioning, Identity Resolution. |
| 🧠 [**AI Architecture**](docs/AI_ARCHITECTURE.md) | Knowledge Graph, Feature Store, Agents, Reasoning. |
| 🛡️ [**Security**](docs/SECURITY.md) | RBAC, SOC2, Compliance Cloud, Workspace Isolation. |
| 🔌 [**API Reference**](docs/API.md) | Public API, Webhooks, CRM API, OAuth2. |
| 🚀 [**Deployment**](docs/DEPLOYMENT.md) | Kubernetes, CI/CD, Multi-Region Failover. |
| 💻 [**Developer Guide**](docs/DEVELOPER_GUIDE.md) | Local Setup, Testing Strategy, Coding Standards. |
| 📈 [**Business Strategy**](docs/BUSINESS.md) | TAM, Pricing, ICP, Competitive Defensibility. |
| ❓ [**FAQ**](docs/FAQ.md) | Frequently Asked Questions. |
| 📖 [**Glossary**](docs/GLOSSARY.md) | Terminology definitions. |

---

## 🛣️ Short Roadmap
- **Q3 2026**: General Availability of the AI Governance Platform.
- **Q4 2026**: Multi-Region K8s Failover deployments.
- **Q1 2027**: Launch of the Enterprise Multi-Agent Platform (Phase 10).

---

## 🤝 Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests to us.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""

LICENSE = """MIT License

Copyright (c) 2026 AVENOR-AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CONTRIBUTING = """# Contributing to AVENOR-AI

Thank you for your interest in contributing to the world's most advanced AI Revenue Intelligence Platform. 

## Workflow
1. **Fork & Clone**: Fork the repository and clone it locally.
2. **Branching**: Create a new branch (`feature/your-feature` or `bugfix/issue-description`).
3. **Clean Architecture**: Ensure your code strictly adheres to the Domain-Driven Design layout. Do not allow Infrastructure logic to leak into Application layers.
4. **Testing**: You must write unit tests. Run `pytest tests/ -v`. A 100% pass rate is required.
5. **Pull Requests**: Submit a PR to the `main` branch. Ensure the CI pipeline passes.

## Development Setup
Please see the [Developer Guide](docs/DEVELOPER_GUIDE.md) for instructions on running the local Docker stack.

## Reporting Issues
Use GitHub Issues to report bugs or request features. Please include environment details, reproduction steps, and expected outcomes.
"""

CHANGELOG = """# Changelog

All notable changes to the AVENOR-AI platform will be documented in this file.

## [1.0.0] - 2026-08-01 - Global Certification Release
- **Phase 9.10**: Completed the final Intelligence Cloud global audit.
- **Phase 9.9**: Deployed AI Governance (Hallucination Detection, HITL).
- **Phase 8.0**: Deployed Revenue Platform Ecosystem (Marketplace, Workflows).
- **Phase 7.0**: Deployed Enterprise Intelligence Cloud (12 Data Engines).
- **Phase 6.0**: Deployed Advanced AI Agent Platform.
- **Phase 5.0**: Deployed Prediction Engine (Scoring).
- **Phase 4.0**: Migrated to FastAPI Backend Intelligence.
- **Phase 3.0**: Built the AI Copilot.
- **Phase 2.0**: Engineered the Revenue OS CRM.
- **Phase 1.0**: Initialized Design System.
"""

CODE_OF_CONDUCT = """# Code of Conduct

## Our Pledge
We pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Our Standards
Examples of behavior that contributes to a positive environment for our community include:
- Demonstrating empathy and kindness toward other people
- Being respectful of differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive feedback

## Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the community leaders responsible for enforcement at `conduct@avenor.ai`.
"""

# ---------------------------------------------------------
# DOCS FILES (HEAVILY STRUCTURED)
# ---------------------------------------------------------

DOCS = {
    "ARCHITECTURE.md": """[🏠 Home](../README.md) | [Next: Modules ➡️](MODULES.md)
<br>

# Architecture Overview

AVENOR-AI is built on a highly modular, scalable, and secure microservices-oriented architecture using **Clean Architecture** principles and **Domain-Driven Design (DDD)**.

## Table of Contents
1. [System Design & Data Flow](#system-design--data-flow)
2. [Technology Stack](#technology-stack)
3. [Repository Structure](#repository-structure)

---

## 1. System Design & Data Flow

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[React/Next.js UI]
        CopilotUI[AI Copilot Interface]
    end
    subgraph "API Gateway Layer"
        Gateway[FastAPI Edge Gateway]
    end
    subgraph "Application Layer"
        RevenueOS[Revenue OS]
        Workflow[Workflow Engine]
        Agents[Agent Platform]
    end
    subgraph "Data Storage"
        PG[(PostgreSQL)]
        Vector[(Vector DB)]
    end
    UI --> Gateway
    Gateway --> RevenueOS
    Gateway --> Agents
    RevenueOS --> PG
    Agents --> Vector
```

## 2. Technology Stack

| Domain | Technology | Justification |
|--------|------------|---------------|
| **Frontend** | React / Next.js | Component-driven architecture, SSR. |
| **Backend API** | Python / FastAPI | Native asynchronous support, ML integration. |
| **Database** | PostgreSQL | ACID compliance, transactional integrity. |
| **Caching** | Redis | Rate limiting, fast memory context. |
| **Infrastructure**| Kubernetes | Multi-region scaling and isolation. |

## 3. Repository Structure

```text
Avenor-AI/
├── app/                        # Main Application Code
│   ├── modules/                # Domain-Driven Modules (e.g. ai_governance)
│   ├── core/                   # Global cross-cutting concerns
│   └── main.py                 # Entrypoint
├── frontend/                   # React/Next.js Application
├── tests/                      # Global Test Suite
├── docs/                       # Official Documentation Suite
└── infrastructure/             # Terraform / K8s manifests
```

<br>

---
[🏠 Home](../README.md) | [Next: Modules ➡️](MODULES.md)
""",

    "MODULES.md": """[⬅️ Prev: Architecture](ARCHITECTURE.md) | [🏠 Home](../README.md) | [Next: Roadmap ➡️](ROADMAP.md)
<br>

# Core Platform Modules

AVENOR-AI is composed of highly specialized modules that work in concert.

## Table of Contents
1. [Revenue OS](#revenue-os)
2. [Enterprise Intelligence](#enterprise-intelligence)
3. [Extensibility](#extensibility)

---

## 1. Revenue OS
The central operating system replaces legacy CRM interfaces.
- **Lead Management**: Dynamic routing.
- **Pipeline Management**: Kanban-style drag-and-drop boards.
- **Forecasting**: Mathematically rigorous revenue forecasting.

## 2. Enterprise Intelligence
12 distinct intelligence engines (Company, Contact, Technology, Buying Committee, Funding, Hiring, Executive, Competitive, Market, Industry, Global Signal, Identity Resolution).

## 3. Extensibility
- **Marketplace**: Install third-party integrations via OAuth.
- **Workflow Builder**: Node-based automation canvas.
- **Agent Builder**: Configure autonomous AI actors.
- **Prompt Studio**: IDE for testing and deploying LLM prompts.

<br>

---
[⬅️ Prev: Architecture](ARCHITECTURE.md) | [🏠 Home](../README.md) | [Next: Roadmap ➡️](ROADMAP.md)
""",

    "ROADMAP.md": """[⬅️ Prev: Modules](MODULES.md) | [🏠 Home](../README.md) | [Next: Database ➡️](DATABASE.md)
<br>

# Complete Platform Roadmap

## Table of Contents
1. [Completed Phases (1-9)](#completed-phases-1-9)
2. [Phase 10: Future Vision](#phase-10-future-vision)
3. [Long-Term Strategy (3-5 Years)](#long-term-strategy-3-5-years)

---

## 1. Completed Phases (1-9)
- **Phase 1-3**: Design System, Revenue OS, AI Copilot.
- **Phase 4-6**: FastAPI Backend, Scoring Engine, Advanced AI Agents.
- **Phase 7-9**: Enterprise Intelligence Cloud, Ecosystem, Global Data Platform, AI Governance.

## 2. Phase 10: Future Vision
The ultimate architectural destination: evolving into a globally connected, federated intelligence network. Includes Autonomous SDRs, Revenue Simulation Engines, and Industry Foundation Models.

## 3. Long-Term Strategy (3-5 Years)
- **Year 1**: Solidify Multi-Region infrastructure; achieve 99.99% SLAs.
- **Year 2-3**: Deploy the Revenue Simulation Engine; establish federated data exchange.
- **Year 4-5**: Reach global ubiquity as the standard AI OS for Revenue Operations.

<br>

---
[⬅️ Prev: Modules](MODULES.md) | [🏠 Home](../README.md) | [Next: Database ➡️](DATABASE.md)
""",

    "DATABASE.md": """[⬅️ Prev: Roadmap](ROADMAP.md) | [🏠 Home](../README.md) | [Next: AI Architecture ➡️](AI_ARCHITECTURE.md)
<br>

# Database Architecture

## Table of Contents
1. [Persistence Technologies](#persistence-technologies)
2. [ER Diagram](#er-diagram)
3. [Scaling & Sharding](#scaling--sharding)

---

## 1. Persistence Technologies
- **PostgreSQL**: Transactional data (Users, Billing, CRM Pipeline).
- **Vector DB**: High-dimensional embeddings and Knowledge Graph relationships.
- **Redis**: Rate limiting, caching, and background queues.

## 2. ER Diagram

```mermaid
erDiagram
    WORKSPACE ||--o{ USER : contains
    WORKSPACE ||--o{ LEAD : manages
    WORKSPACE ||--o{ COMPLIANCE_LOG : audits
```

## 3. Scaling & Sharding
- **Horizontal Partitioning**: PostgreSQL partitioned by `workspace_id`.
- **Time-Series Partitioning**: Append-only tables partitioned by month for easy TTL drops.
- **Active-Passive**: Cross-region database replication for zero downtime disaster recovery.

<br>

---
[⬅️ Prev: Roadmap](ROADMAP.md) | [🏠 Home](../README.md) | [Next: AI Architecture ➡️](AI_ARCHITECTURE.md)
""",

    "AI_ARCHITECTURE.md": """[⬅️ Prev: Database](DATABASE.md) | [🏠 Home](../README.md) | [Next: Security ➡️](SECURITY.md)
<br>

# AI Architecture & Knowledge Graph

## Table of Contents
1. [Knowledge Graph](#knowledge-graph)
2. [Agent Platform](#agent-platform)
3. [Foundation Models & Feature Store](#foundation-models--feature-store)
4. [AI Governance (Constitutional AI)](#ai-governance-constitutional-ai)

---

## 1. Knowledge Graph
Vector-native graph tracking `Nodes` (Companies, People), `Edges` (Relationships), and `Signals`. Employs Identity Resolution to merge fragmented global data mathematically.

## 2. Agent Platform
Agents are specialized cognitive loops. They execute a Plan, utilize Tools (APIs), and rely on short/long-term Memory.

## 3. Foundation Models & Feature Store
Not all AI is generative. Binary classifiers use the **Feature Store** to retrieve real-time mathematical entity vectors (e.g., `company_momentum`).

## 4. AI Governance (Constitutional AI)
All AI outputs pass through strict gates:
- **Hallucination Detection**: Un-grounded facts are strictly blocked.
- **Human-In-The-Loop**: High-risk actions are intercepted into a `PENDING` queue awaiting human authorization.

<br>

---
[⬅️ Prev: Database](DATABASE.md) | [🏠 Home](../README.md) | [Next: Security ➡️](SECURITY.md)
""",

    "SECURITY.md": """[⬅️ Prev: AI Architecture](AI_ARCHITECTURE.md) | [🏠 Home](../README.md) | [Next: API ➡️](API.md)
<br>

# Security, Trust, & Compliance

## Table of Contents
1. [Tenant Isolation](#tenant-isolation)
2. [Encryption & Secrets](#encryption--secrets)
3. [Compliance Cloud (SOC2 / GDPR)](#compliance-cloud-soc2--gdpr)

---

## 1. Tenant Isolation
Every database query strictly filters by `workspace_id`. Cross-tenant data leakage is structurally impossible. RBAC controls individual human permissions.

## 2. Encryption & Secrets
- **In-Transit**: TLS 1.3.
- **At-Rest**: AES-256 for PostgreSQL and Vector databases.
- **Secrets**: Envelope Encryption via KMS.

## 3. Compliance Cloud (SOC2 / GDPR)
- **Data Classification**: Tags PII and enforces strict Time-to-Live (TTL) deletion policies.
- **GDPR**: Natively processes DSAR Right to Erasure requests across all relational and vector databases.
- **SOC2 Audit**: Maintains continuous cryptographic logs of all actions, including AI decisions.

<br>

---
[⬅️ Prev: AI Architecture](AI_ARCHITECTURE.md) | [🏠 Home](../README.md) | [Next: API ➡️](API.md)
""",

    "API.md": """[⬅️ Prev: Security](SECURITY.md) | [🏠 Home](../README.md) | [Next: Deployment ➡️](DEPLOYMENT.md)
<br>

# API Reference

## Table of Contents
1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [SDKs & Webhooks](#sdks--webhooks)

---

## 1. Authentication
- **API Keys**: For server-to-server (`Authorization: Bearer av_prod_xxx`).
- **OAuth2**: For marketplace integrations with granular scopes.

## 2. Core Endpoints
- `/crm`: Manage Leads and Opportunities.
- `/intelligence`: Query the Knowledge Graph and global signals.
- `/ai`: Execute autonomous agents and evaluate prompts.
- `/workflows`: Trigger automations.
- `/marketplace`: Install apps and sync data.

## 3. SDKs & Webhooks
- Official SDKs: Python (`avenor-ai`) and Node.js (`@avenor/ai`).
- `/webhooks/subscribe`: Listen for events like `deal.won` or `agent.requires_approval`.

<br>

---
[⬅️ Prev: Security](SECURITY.md) | [🏠 Home](../README.md) | [Next: Deployment ➡️](DEPLOYMENT.md)
""",

    "DEPLOYMENT.md": """[⬅️ Prev: API](API.md) | [🏠 Home](../README.md) | [Next: Developer Guide ➡️](DEVELOPER_GUIDE.md)
<br>

# Deployment & Infrastructure Guide

## Table of Contents
1. [Cloud Native Deployments](#cloud-native-deployments)
2. [Multi-Region Scaling](#multi-region-scaling)
3. [CI/CD & Observability](#cicd--observability)

---

## 1. Cloud Native Deployments
AVENOR-AI is containerized. Production workloads are orchestrated via **Kubernetes (EKS/GKE/AKS)**, provisioned entirely via Terraform.

## 2. Multi-Region Scaling
- **Geo-Routing**: Anycast routes traffic to the physically nearest datacenter.
- **Failover**: Automated Active-Passive replication ensures seamless disaster recovery if a region goes offline.

## 3. CI/CD & Observability
- **Pipeline**: GitHub Actions runs tests -> builds containers -> deploys via ArgoCD (Rolling Updates).
- **Observability**: Prometheus metrics, Grafana dashboards, and OpenTelemetry distributed tracing ensure 100% visibility into AI latency.

<br>

---
[⬅️ Prev: API](API.md) | [🏠 Home](../README.md) | [Next: Developer Guide ➡️](DEVELOPER_GUIDE.md)
""",

    "DEVELOPER_GUIDE.md": """[⬅️ Prev: Deployment](DEPLOYMENT.md) | [🏠 Home](../README.md) | [Next: Business ➡️](BUSINESS.md)
<br>

# Developer & Testing Guide

## Table of Contents
1. [Local Setup](#local-setup)
2. [Coding Standards](#coding-standards)
3. [Testing Strategy](#testing-strategy)

---

## 1. Local Setup
Ensure you have Docker and Python 3.12+ installed.
```bash
docker-compose up -d
python -m venv venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 2. Coding Standards
We enforce **Clean Architecture**. Domain models (`app/modules/domain`) must never import from Infrastructure (`app/modules/infrastructure`). Feature branches must stem from `main`.

## 3. Testing Strategy
- **Unit**: Isolated domain logic (mocked DB).
- **Integration**: Database transactions and Celery workers.
- **E2E**: Playwright browser emulation.
- **AI**: The `test_ai_governance.py` suite explicitly verifies Hallucination detection.
- **Chaos**: Randomly killing pods to verify failover integrity.

<br>

---
[⬅️ Prev: Deployment](DEPLOYMENT.md) | [🏠 Home](../README.md) | [Next: Business ➡️](BUSINESS.md)
""",

    "BUSINESS.md": """[⬅️ Prev: Developer Guide](DEVELOPER_GUIDE.md) | [🏠 Home](../README.md) | [Next: FAQ ➡️](FAQ.md)
<br>

# Business, Market, & Competitive Strategy

## Table of Contents
1. [Target Customers & Pricing](#target-customers--pricing)
2. [Competitive Landscape](#competitive-landscape)
3. [The Moat](#the-moat)

---

## 1. Target Customers & Pricing
- **ICP**: Mid-Market to Enterprise ($50M - $1B+ ARR), CROs, VP Sales.
- **Revenue Model**: Hybrid SaaS (Platform seats) + Consumption (LLM/Agent execution usage).

## 2. Competitive Landscape
- **ZoomInfo / Apollo**: Legacy static databases vs. AVENOR's dynamic Knowledge Graph and autonomous execution.
- **Salesforce**: System of record requiring manual entry vs. AVENOR's system of intelligence that autonomously populates pipeline.
- **Clari**: Historical forecasting vs. AVENOR's real-time external signal predictive forecasting.

## 3. The Moat
Defensibility lies in **Collective Intelligence**. As autonomous agents uncover successful patterns, they are mathematically anonymized into Industry Foundation Models, allowing the entire global platform to learn and optimize continuously.

<br>

---
[⬅️ Prev: Developer Guide](DEVELOPER_GUIDE.md) | [🏠 Home](../README.md) | [Next: FAQ ➡️](FAQ.md)
""",

    "FAQ.md": """[⬅️ Prev: Business](BUSINESS.md) | [🏠 Home](../README.md) | [Next: Glossary ➡️](GLOSSARY.md)
<br>

# Frequently Asked Questions (FAQ)

### 1. Does AVENOR-AI replace Salesforce?
Not necessarily on day one. Our Integration Hub synchronizes bi-directionally with Salesforce. Most enterprises start by using AVENOR as their Intelligence Cloud and Autonomous Agent executor, before fully migrating off legacy CRMs.

### 2. Is my enterprise data used to train AI models for competitors?
No. All data is strictly isolated within your Workspace. Any global learning is performed strictly on mathematically anonymized vectors without PII, explicitly governed by our Compliance Cloud.

### 3. What LLM does AVENOR-AI use?
We use a polyglot architecture. The Agent Builder seamlessly routes tasks to OpenAI (GPT-4), Anthropic (Claude), or our proprietary in-house Foundation Revenue Models, depending on the computational requirement.

### 4. Can the AI send emails without my permission?
No. High-risk actions (like sending external communications or terminating contracts) are strictly governed by the AI Governance Engine, which forces the action into a Human-In-The-Loop approval queue.

<br>

---
[⬅️ Prev: Business](BUSINESS.md) | [🏠 Home](../README.md) | [Next: Glossary ➡️](GLOSSARY.md)
""",

    "GLOSSARY.md": """[⬅️ Prev: FAQ](FAQ.md) | [🏠 Home](../README.md)
<br>

# Platform Glossary

- **Agent**: An autonomous AI loop capable of planning and executing multi-step goals using provided tools.
- **Constitutional AI**: The safety framework that ensures agents operate within ethical, factual, and policy constraints.
- **DSAR**: Data Subject Access Request (GDPR compliance).
- **Feature Store**: Centralized registry that computes and serves machine learning features in real-time to prevent training-serving skew.
- **Knowledge Graph**: A vector-native database that maps entities (companies, people) and their mathematical relationships.
- **Identity Resolution**: The algorithmic process of merging fragmented global data signals into a single canonical entity.
- **Revenue OS**: The user-facing interface that replaces legacy CRM dashboards.

<br>

---
[⬅️ Prev: FAQ](FAQ.md) | [🏠 Home](../README.md)
"""
}

# WRITE ROOT FILES
with open(os.path.join(ROOT_DIR, "README.md"), "w", encoding="utf-8") as f: f.write(README)
with open(os.path.join(ROOT_DIR, "LICENSE"), "w", encoding="utf-8") as f: f.write(LICENSE)
with open(os.path.join(ROOT_DIR, "CONTRIBUTING.md"), "w", encoding="utf-8") as f: f.write(CONTRIBUTING)
with open(os.path.join(ROOT_DIR, "CHANGELOG.md"), "w", encoding="utf-8") as f: f.write(CHANGELOG)
with open(os.path.join(ROOT_DIR, "CODE_OF_CONDUCT.md"), "w", encoding="utf-8") as f: f.write(CODE_OF_CONDUCT)

# WRITE DOC FILES
for filename, content in DOCS.items():
    with open(os.path.join(DOCS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

# ZIP EVERYTHING
zip_path = os.path.join(ROOT_DIR, "AVENOR-AI-Documentation.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(ROOT_DIR, "README.md"), "README.md")
    zf.write(os.path.join(ROOT_DIR, "LICENSE"), "LICENSE")
    zf.write(os.path.join(ROOT_DIR, "CONTRIBUTING.md"), "CONTRIBUTING.md")
    zf.write(os.path.join(ROOT_DIR, "CHANGELOG.md"), "CHANGELOG.md")
    zf.write(os.path.join(ROOT_DIR, "CODE_OF_CONDUCT.md"), "CODE_OF_CONDUCT.md")
    
    for filename in DOCS.keys():
        file_path = os.path.join(DOCS_DIR, filename)
        zf.write(file_path, f"docs/{filename}")

print(f"Successfully generated and zipped {zip_path}")
