[⬅️ Prev: Deployment](DEPLOYMENT.md) | [🏠 Home](../README.md) | [Next: Business ➡️](BUSINESS.md)
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
