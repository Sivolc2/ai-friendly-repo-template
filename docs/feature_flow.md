# Feature Development Workflow

This document outlines the step-by-step process for developing new features in this repository, emphasizing collaboration with AI assistants.

| Step | Command / action | Output & gate | AI Assistance Notes |
|------|------------------|---------------|---------------------|
| **1. Understand & Plan** | Review existing `registry/` context, relevant `README_*.md` files. Discuss requirements. | Clear understanding of feature scope and impact. | Use AI to explore existing codebase via `registry/` context to identify reusable components/functions. |
| **2. Draft PRD** | Create `docs/prd/NNN-<slug>.md`. Use `code_builder/main_orchestrator.sh "feature description"` or manually write PRD. | PRD must list: Goals, User Stories (if any), Detailed Technical Plan (functions, data schemas, pipeline flow, adapters needed), Acceptance Criteria. | AI can generate the initial PRD draft. Human reviews and refines it. | 
| **3. Scaffold Feature** | `pnpm new:feature <slug>` (once script is ready) or manually create directories and stub files. | Stub directories/files for functions, pipelines, tests, components. | AI can generate stub files based on the PRD's technical plan. |
| **4. Write Tests (TDD approach recommended)** | Author unit tests for pure functions (`repo_src/backend/functions/`, `repo_src/frontend/src/utils/`) and integration tests for pipelines/components. | CI must show initial test failures (Red). | AI can help generate test cases based on function/component specifications in the PRD and acceptance criteria. |
| **5. Implement Pure Functions & UI Components** | Write code in `repo_src/backend/functions/` and `repo_src/frontend/src/{components,hooks,utils}/`. Ensure tests pass. | `pnpm test` ✔ (Green for unit tests). | AI implements functions/components based on PRD and its understanding of existing patterns from the golden path app. Human reviews and iterates with AI. |
| **6. Compose Pipeline / Wire UI** | Backend: Add orchestrator in `repo_src/backend/pipelines/`. Frontend: Integrate components into pages, manage state, connect to services. Ensure tests pass. | Pipeline tests green. UI interactions work as expected. | AI helps compose pipelines or wire UI elements, referencing the PRD's flow. |
| **7. Implement Adapters / API Services** | Backend: (If needed) add side-effect impl in `repo_src/backend/adapters/`. Frontend: Implement calls in `repo_src/frontend/src/services/`. | Integration tests green. API communication works. | AI can generate adapter/service code based on external API contracts or DB schema definitions. |
| **8. Sync Docs & Registry** | `pnpm ctx:sync` (or `pnpm registry:update`) | No drift detected in `registry/`. | AI (if capable through an agent) could be prompted to update related `README_*.md` docstrings if significant changes were made. Otherwise, human responsibility. |
| **9. Manual E2E & QA** | Manually test the feature flow. Run E2E tests: `pnpm e2e`. | Feature works as per acceptance criteria. E2E tests pass. | - |
| **10. Open PR** | Create Pull Request. Describe changes, link to PRD. | - | AI can help summarize changes for the PR description based on commits. |
| **11. Code Review** | Human team members review the PR. | Code quality, adherence to patterns, correctness. | - |
| **12. Merge** | Merge PR after approval and passing CI. | CI: lint, type, test, ctx sync. | - |
