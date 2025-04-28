# Feature Implementation Rules

## New Feature Process

1. Create feature slice using `pnpm new-feature <backend|frontend> <slice-name>`
2. Review implementation guide in `packages/<backend|frontend>/README_implementation_guide.md`
3. Update the `README_{slice-name}.md` with proper Overview and Implementation Details
4. Implement feature following SOLID principles
5. Add tests
6. Run `pnpm gen:context <backend|frontend>`
7. Submit PR

## Modifying Existing Features

1. Review the existing `README_{slice-name}.md` to understand current functionality
2. Make changes following SOLID principles
3. Update tests
4. Update README if architecture changes
5. Run `pnpm gen:context <backend|frontend>`
6. Submit PR

## Code Organization

### Backend
- Keep services focused and small (≤200 LOC)
- Use dependency injection
- Follow hexagonal architecture
- Write comprehensive tests

### Frontend
- Keep components focused and small (≤200 LOC)
- Use hooks for business logic
- Follow atomic design
- Write comprehensive tests

## Documentation

### README_{slice-name}.md
- Overview: Purpose and functionality
- Architecture: Data flow and component structure
- Public API: Exported functions and types
- Implementation Details: Notes and considerations

### Code Comments
- Use docstrings for public APIs
- Include type hints
- Document complex logic
