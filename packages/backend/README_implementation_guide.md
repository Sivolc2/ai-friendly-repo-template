# Backend Implementation Guide

## When to add a **module** vs. edit core

### Add a module when:
- Implementing a new feature that can be isolated
- Creating a new integration with external services
- Adding domain-specific business logic

### Edit core when:
- Modifying shared infrastructure
- Updating common utilities
- Changing core interfaces

## Scaffold a feature slice

```bash
pnpm new-feature backend <slice-name>
```

### Five required steps
1. Fill Overview in README_{slice-name}.md
2. Implement service logic (≤200 LOC per class)
3. Expose via `register(app)`
4. Update shared schemas if needed
5. Run `pnpm gen:context backend`

## Directory Structure
```
modules/
├── _template/
│   ├── __init__.py
│   ├── service.py
│   ├── types.py
│   └── tests/
│       ├── __init__.py
│       └── test_service.py
└── your_feature/
    ├── README_your_feature.md
    ├── __init__.py
    ├── service.py
    ├── types.py
    └── tests/
        ├── __init__.py
        └── test_service.py
```

## Module Structure
```
modules/
  ├── _template/           # Template for new modules
  ├── core/               # Core functionality
  ├── adapters/           # External service integrations
  └── {feature-name}/     # Feature-specific modules
      ├── README_your_feature.md
      ├── __init__.py
      ├── service.py
      ├── types.py
      └── tests/
          ├── __init__.py
          └── test_service.py
```

## Python Best Practices
- Use type hints throughout the codebase
- Follow PEP 8 style guide
- Use dataclasses for data structures
- Implement async/await for I/O operations
- Use dependency injection for services

## Testing
- Unit tests required for all new code (pytest)
- Integration tests for external service interactions
- Performance tests for critical paths
- Type checking with mypy
- Code formatting with black 