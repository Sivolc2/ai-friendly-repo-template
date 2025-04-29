# AI-Friendly Repository Template

A framework for collaborative content creation and management with an AI-driven, functional-core architecture.

## 📋 Overview

This repository is structured as a monorepo with a clean separation between pure functions (functional core) and side effects (adapters/IO). This architecture makes it particularly friendly for AI-assisted development and reasoning.

## 🏗️ Project Structure

```
.
├── packages
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
```

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install              # Frontend dependencies
source .venv/bin/activate # Activate Python virtual environment
pip install -r packages/backend/requirements.txt

# Run development servers
pnpm --filter frontend dev      # Start Vite dev server
uvicorn packages.backend.main:app --reload  # Start backend server

# Development workflow
pnpm lint                # Run linters
pnpm typecheck           # Run type checking
pnpm test                # Run tests
pnpm ctx:sync            # Update documentation
pnpm diagrams:generate   # Generate function & pipeline diagrams
```

## 📝 Development Flow

See [docs/feature_flow.md](docs/feature_flow.md) for the step-by-step process for adding new features.

## 📚 Documentation

Each directory contains a README file with specific guidance for that component.

### Registry

The [registry](registry/) directory contains auto-generated documentation and indexes that provide AI-friendly context:

- **backend_context.md**: Concise index of backend functionality
- **frontend_context.md**: Concise index of frontend components and functions
- **pipeline_context.md**: Summary of all pipelines in the application
- **context.json**: Machine-readable metadata for AI tools

To update the registry:

```bash
pnpm ctx:sync
```

### Diagrams

The [docs/diagrams](docs/diagrams/) directory contains automatically generated diagrams that visualize:

- **Function Overview**: All functions from the `functions/` directory grouped by module
- **Pipeline Diagrams**: Individual pipeline functions and their relationships

To generate or update diagrams:

```bash
pnpm diagrams:generate
```

## 🔄 CI/CD

The project uses GitHub Actions for continuous integration and deployment.

## 📄 License

ISC
