# Contributing to AVENOR-AI

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
