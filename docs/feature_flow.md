# Feature Development Workflow

This document outlines the step-by-step process for developing new features in this repository.

| Step | Command / action | Output & gate |
|------|------------------|---------------|
| **1. Draft PRD** | Create `docs/prd/NNN-<slug>.md` using registry of functions (reuse where possible) + guides | Must list *acceptance criteria* |
| **2. Red tests** | Author unit tests in `backend/tests/<slug>/` | CI must show failures |
| **3. Implement** | Write pure functions until tests pass | `pnpm test` ✔ |
| **4. Compose pipeline** | Add orchestrator in `pipelines/` | Pipeline tests green |
| **5. Wire adapters** | (If needed) add side-effect impl in `adapters/` | Integration tests green |
| **6. Sync docs** | `pnpm ctx:sync` | No drift detected |
| **7. Open PR** | - | CI: lint, type, test, ctx |
| **8. Merge** | - | Done |

## Design Differences

- This workflow follows the principle of "outside-in" TDD (Test-Driven Development) 
- Pure functions are implemented first, then composed into pipelines
- Side effects (database, HTTP, etc.) are isolated in adapter modules
- Documentation is generated automatically from code and kept in sync via CI 