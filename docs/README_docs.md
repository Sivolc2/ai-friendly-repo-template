# Documentation

This directory contains project documentation, including:

- **Architecture Decision Records (ADRs)**: Documenting significant architectural decisions
- **Product Requirements Documents (PRDs)**: Defining features and requirements
- **Diagrams**: System and component diagrams
- **Pipelines**: Auto-generated documentation from code

## Documentation Structure

```
docs/
├── adr/                 # Architecture Decision Records
├── prd/                 # Product Requirements Documents
├── diagrams/            # System diagrams and visual documentation
├── pipelines/           # Auto-generated documentation
│   └── functions.md     # Catalog of functions from codebase
└── README_docs.md       # This file
```

## Documentation Generation

Some documentation is generated automatically from the codebase:

```bash
# Generate context and documentation
pnpm ctx:sync
```

This command:
1. Scans the codebase for functions and their docstrings
2. Generates a human-readable Markdown catalog
3. Produces a machine-readable JSON file for AI tools

## MkDocs Setup (Optional)

This project can be configured to use MkDocs to create a documentation site:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve documentation locally
pnpm docs:serve

# Build documentation site
pnpm docs:build
```

## Documentation Guidelines

1. **Keep documentation close to code**: README files should be in the directories they describe
2. **Use Markdown**: All documentation should be in Markdown format
3. **Link between documents**: Use relative links to connect related documentation
4. **Update regularly**: Keep documentation in sync with code changes
5. **Auto-generate where possible**: Use scripts to generate documentation from code

## Design Differences

- Documentation is treated as a first-class citizen in the repository
- Auto-generation scripts keep documentation in sync with code
- ADRs capture architectural decisions and their rationale
- README files are included at every level of the repository 