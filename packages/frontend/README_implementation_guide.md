# Frontend Implementation Guide

## When to add a **feature** vs. edit shared

### Add a feature when:
- Implementing a new user-facing feature
- Creating a new view or component
- Adding feature-specific state management

### Edit shared when:
- Modifying common components
- Updating shared utilities
- Changing global state management

## Scaffold a feature slice

```bash
pnpm new-feature frontend <slice-name>
```

### Five required steps
1. Fill Overview in README_{slice-name}.md
2. Implement components and hooks (≤200 LOC per file)
3. Export via index.ts
4. Update shared types if needed
5. Run `pnpm gen:context frontend`

## Directory Structure
```
features/
├── _template/
│   ├── components/
│   ├── hooks/
│   ├── index.ts
│   └── types.ts
└── your_feature/
    ├── README_your_feature.md
    ├── components/
    ├── hooks/
    ├── index.ts
    └── types.ts
```

## Testing
- Component tests required for all new UI code
- Hook tests for custom React hooks
- Integration tests for feature workflows
- E2E tests for critical user journeys 