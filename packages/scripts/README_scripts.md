# Scripts

This directory contains utility scripts for development and automation.

## Available Scripts

### Feature Scaffolding

```bash
# Usage
pnpm new:feature <slug>

# Example
pnpm new:feature user-management
```

**Description**: Creates the necessary directory structure and starter files for a new feature, including:
- Backend function, pipeline, and adapter directories
- Frontend component, page, and service directories
- A test file with a basic test structure
- A data model file
- A PRD file for documenting requirements

### Context Export

```bash
# Usage
pnpm ctx:sync
```

**Description**: Scans the codebase for functions and their docstrings, generating:
- A human-readable Markdown catalog in `docs/pipelines/functions.md`
- A machine-readable JSON file in `context/context.json` for AI tools

## Adding New Scripts

When adding a new script:
1. Place the script in this directory
2. Add an entry to the scripts section in the root package.json
3. Document the script in this README
4. Ensure it follows project coding standards

## Design Principles

Scripts in this directory should:
1. Be well-documented with clear usage instructions
2. Handle errors gracefully
3. Provide clear feedback to the user
4. Be cross-platform where possible
5. Follow the same code quality standards as the rest of the project

## Design Differences

- Scripts are treated as proper applications with documentation and error handling
- Scripts follow a functional approach where possible
- Scripts are designed to be reusable and composable 