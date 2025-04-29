# Backend

The backend is built using a functional core architecture, which separates pure functions from side effects. This makes the code more testable, maintainable, and easier to reason about.

## Architecture

```
+----------------+      +---------------+      +----------------+
|                |      |               |      |                |
|    Adapters    | <--> |   Pipelines   | <--> |   Functions    |
|  (Side Effects)|      | (Orchestration|      |  (Pure Logic)  |
|                |      |    Layer)     |      |                |
+----------------+      +---------------+      +----------------+
        ^                                              ^
        |                                              |
        v                                              v
+----------------+                             +----------------+
|                |                             |                |
|    External    |                             |      Data      |
|    Systems     |                             |    Models      |
|                |                             |                |
+----------------+                             +----------------+
```

## Components

- **data/**: Immutable data models and schemas defined using Pydantic
- **functions/**: Pure functions that implement the business logic
- **pipelines/**: Orchestration layer that composes functions
- **adapters/**: Wrappers for side effects (database, HTTP, etc.)
- **utils/**: Generic helper functions
- **tests/**: Unit and integration tests

## Development

```bash
# Activate virtual environment
source ../../.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term
```

## Design Principles

1. **Functional Core, Imperative Shell**: Keep business logic pure, push side effects to the edges
2. **Single Responsibility**: Each function should do one thing well
3. **Dependency Inversion**: High-level modules depend on abstractions, not concrete implementations
4. **Testability**: Pure functions are easy to test without mocks
5. **Documentation**: Docstrings and type hints are required for all functions 