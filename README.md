# AI-Friendly Repository Template

A framework for collaborative content creation and management with an AI-driven, functional-core architecture.

## 🤖 How to Use This Repository with AI

This repository is designed for effective human-AI collaboration. Follow this process:

### Contributing with AI Assistance
1. **Add documentation first**: Create or update guides in `docs/guides/` to document new features or processes
2. **Prompt the AI model with**:
   - `docs/feature_flow.md` - Shows the process for contributing (update as workflows evolve)
   - Registry context files in `registry/` (backend_context.md, frontend_context.md)
3. **Use README files** in each folder as guidance for your contributions
4. **Develop iteratively**: Test features after implementing and check for output

### Best Practices
- **Encode business logic in pipelines**: Expand pipeline documentation to capture domain knowledge
- **Update documentation as you code**: Have your AI assistant update docs as pipelines are implemented
- **Follow testing patterns**: Use the established testing harness for both frontend and backend

## 📋 Overview

This repository is structured as a monorepo with a clean separation between pure functions (functional core) and side effects (adapters/IO). This architecture makes it particularly friendly for AI-assisted development and reasoning.

## 🏗️ Project Structure

```
.
├── repo_src
│   ├── backend            # Python backend with functional core
│   │   ├── adapters/      # DB / HTTP side-effect wrappers
│   │   ├── data/          # immutable schemas/constants
│   │   ├── functions/     # pure functions
│   │   ├── pipelines/     # orchestration layers
│   │   ├── tests/         # unit and integration tests
│   │   ├── utils/         # generic helpers
│   │   ├── main.py        # entrypoint
│   │   └── README_backend.md
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
# One-command project setup
pnpm setup-project       # Install dependencies, create venv, install Python packages, and set up env files

# Or manual step-by-step setup:
pnpm install              # Frontend dependencies
python -m venv .venv      # Create Python virtual environment
source .venv/bin/activate # Activate Python virtual environment
pip install -r repo_src/backend/requirements.txt
pnpm setup-env            # Set up environment variables

# Run development servers
pnpm dev                  # Start both frontend and backend servers (using Turborepo)
pnpm dev:clean            # Reset ports and start dev servers
pnpm dev:frontend         # Run only frontend
pnpm dev:backend          # Run only backend

# Individual commands
pnpm reset                # Kill processes using ports 8000, 5173, and 5174
pnpm --filter frontend dev      # Start Vite dev server
uvicorn repo_src.backend.main:app --reload  # Start backend server

# Development workflow
pnpm lint                # Run linters
pnpm typecheck           # Run type checking
pnpm test                # Run tests for both frontend and backend
pnpm e2e                 # Run end-to-end tests with Playwright
pnpm ci                  # Run lint, typecheck, and tests (CI pipeline)
pnpm refresh-docs        # Update documentation and diagrams
```

## 🧪 Testing

This project uses a comprehensive testing harness that allows running all tests with a single command while keeping each language's tooling isolated:

- **Frontend**: Vitest + React Testing Library
- **Backend**: pytest + hypothesis
- **E2E**: Playwright

See [README.testing.md](README.testing.md) for detailed information about the testing setup.

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
