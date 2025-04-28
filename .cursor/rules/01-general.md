---
description: Framework Zero – General Coding Conventions
globs:
  - "**/*.{py,ts,tsx}"
alwaysApply: true          # always sent with every AI request
---

# 🏗️ Project Structure & Documentation

## Repository Organization
- `docs/` - Project documentation and ADRs
- `packages/` - Backend and frontend code
- `registry/` - Generated documentation and indexes

## Documentation References
- For new features: See `docs/04_feature_implementation_rules.md`
- For shared code changes: See `docs/03_shared_code_rules.md`
- For architecture changes: See `docs/02_rules_of_change.md`

## Key Workflows
- Use `pnpm new-feature` to create new feature slices
- Run `pnpm gen:context` after significant changes
- Keep ADRs in `/docs/adr/YYYYMMDD-slug.md`

## Code Organization
- Backend: `packages/backend/{core,adapters,modules}`
- Frontend: `packages/frontend/src/{shared,app,features}`
- Each module should have its own `README_{folder_name}.md`
