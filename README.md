## Quick Start

```bash
# Install dependencies
pnpm install

# Start development servers
pnpm dev

# Run tests
pnpm test

# Generate documentation
pnpm gen:context
```

## Project Structure

```
.
├── docs/                    # Project documentation
│   ├── 00_project_vision.md    # Project vision and goals
│   ├── 01_architecture_overview.md  # System architecture
│   ├── 02_rules_of_change.md   # Development rules
│   ├── 03_shared_code_rules.md # Shared code guidelines
│   └── 04_feature_implementation_rules.md # Feature development guide
├── packages/
│   ├── backend/            # Backend services
│   │   ├── core/          # Core functionality
│   │   ├── adapters/      # External integrations
│   │   └── modules/       # Feature modules
│   └── frontend/          # Frontend application
│       └── src/
│           ├── app/       # Application shell
│           ├── shared/    # Shared components
│           └── features/  # Feature modules
└── registry/              # Generated documentation
```

## Key Commands

### Development
```bash
# Start development servers
pnpm dev

# Start backend only
pnpm dev:backend

# Start frontend only
pnpm dev:frontend
```

### Feature Development
```bash
# Create new feature
pnpm new-feature <backend|frontend> <feature-name>

# Generate documentation
pnpm gen:context <backend|frontend>

# Update system diagram
pnpm update:diagram
```

### Testing
```bash
# Run all tests
pnpm test

# Run backend tests
pnpm test:backend

# Run frontend tests
pnpm test:frontend
```

## Documentation Guide

### For New Developers
1. Start with `docs/00_project_vision.md` to understand the project goals
2. Read `docs/01_architecture_overview.md` for system architecture
3. Review `docs/02_rules_of_change.md` for development guidelines

### For Feature Development
1. Read `docs/04_feature_implementation_rules.md` for feature development process
2. Review the appropriate implementation guide:
   - Backend: `packages/backend/README_implementation_guide.md`
   - Frontend: `packages/frontend/README_implementation_guide.md`

### For Shared Code Changes
1. Read `docs/03_shared_code_rules.md` for shared code guidelines
2. Review the appropriate module's README:
   - Backend Core: `packages/backend/core/README_core.md`
   - Backend Adapters: `packages/backend/adapters/README_adapters.md`
   - Frontend App: `packages/frontend/src/app/README_app.md`
   - Frontend Shared: `packages/frontend/src/shared/README_shared.md`

## Development Workflow

1. **Create Feature**
   ```bash
   pnpm new-feature <backend|frontend> <feature-name>
   ```

2. **Implement Feature**
   - Follow the implementation guide
   - Write tests
   - Update documentation

3. **Generate Documentation**
   ```bash
   pnpm gen:context <backend|frontend>
   ```

4. **Submit PR**
   - Include documentation updates
   - Link to relevant ADRs if needed
   - Ensure tests pass

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the development workflow
4. Submit a pull request

## License

[Add your license information here] 