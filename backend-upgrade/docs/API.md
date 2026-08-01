[⬅️ Prev: Security](SECURITY.md) | [🏠 Home](../README.md) | [Next: Deployment ➡️](DEPLOYMENT.md)
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
