[⬅️ Prev: AI Architecture](AI_ARCHITECTURE.md) | [🏠 Home](../README.md) | [Next: API ➡️](API.md)
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
