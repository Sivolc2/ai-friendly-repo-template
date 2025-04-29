# Testing Harness

This project uses a comprehensive testing harness for both frontend and backend components. The setup allows running all tests with a single command while keeping each language's tooling isolated.

## Testing Layers

| Layer | Package(s) | Framework | What it checks |
|-------|------------|-----------|----------------|
| **Unit** | backend | **pytest + hypothesis** | Pure‐function behaviour, property cases |
| | frontend | **Vitest + @testing-library/react** | Components, hooks, pure helpers |
| **Pipeline / integration** | backend | **pytest-asyncio** | Orchestrators calling faked ports |
| **API** | backend ↔ frontend | **Schemathesis** (optional) | API contract validation |
| **E2E** | root | **Playwright** | Browser flows against the application |

## Environment Setup

This project uses separate `.env` files for frontend and backend:

1. For frontend: `repo_src/frontend/.env`
2. For backend: `repo_src/backend/.env`

To set up your environment:
```bash
# Copy the default environment variables
cp .env.defaults repo_src/frontend/.env
cp .env.defaults repo_src/backend/.env
```

Make any necessary adjustments to the `.env` files for your local development environment.

## Running Tests

### All Tests
```bash
pnpm test
```

### Individual repo_src
```bash
# Frontend tests
pnpm --filter frontend test

# Backend tests
pnpm --filter backend test
```

### End-to-End Tests
```bash
pnpm e2e
```

## Development Setup

1. Install dependencies:
```bash
pnpm i
```

2. Set up Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r repo_src/backend/requirements.txt
```

3. Run all checks:
```bash
pnpm ci  # Runs lint → typecheck → tests
```

## Design Differences

This testing harness follows the pattern described in the [testing_harness.md](docs/guides/testing_harness.md) guide with a few adjustments:

1. **Separate .env Files**: Instead of using a central .env file with namespacing, we use separate .env files for frontend and backend for better isolation.
2. **Package Manager**: Uses pnpm workspaces for efficient dependency management.
3. **Playwright Config**: Includes a comprehensive Playwright configuration for E2E testing that manages both frontend and backend services. 