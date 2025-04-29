---
description: Framework Zero – General Coding Conventions
globs:
  - "**/*.{py,ts,tsx}"     # These patterns enable Cursor to automatically apply the rule when relevant files are referenced or edited
alwaysApply: true          # always sent with every AI request
---

# 🏗️ Project Structure & Documentation

## Repository Organization
├── repo_src
│   ├── backend            # Python backend with functional core
│   │   ├── adapters/      # DB / HTTP side-effect wrappers
│   │   ├── data/          # immutable schemas/constants
│   │   ├── functions/     # pure functions
│   │   ├── pipelines/     # orchestration layers
│   │   ├── tests/         # unit and integration tests
│   │   ├── utils/         # generic helpers
│   │   ├── main.py        # entrypoint
│   ├── frontend           # React/TypeScript frontend
│   │   ├── src/
│   │   │   ├── components/  # reusable UI components
│   │   │   ├── hooks/       # custom React hooks
│   │   │   ├── pages/       # route-level components
│   │   │   ├── services/    # API clients and services
│   │   │   ├── types/       # TypeScript type definitions
│   │   │   └── utils/       # utility functions
│   │   └── README_frontend.md
│   ├── scripts            # developer tooling and utilities
│   └── shared             # shared types and utilities
│       └── README_shared.md
├── docs
│   ├── adr/             # architecture decision records
│   ├── diagrams/        # system and component diagrams
│   ├── pipelines/       # auto-generated pipeline documentation
│   ├── prd/             # product requirements documents
│   └── README_*.md      # documentation guides
├── registry/            # auto-generated documentation and indexes
└── .github/workflows    # CI/CD configuration
All exisiting folders will have a README_{folder_name}. At Repository Organization level, each will have a README explaining conditions for adding code to that section. Please reference before adding code.

