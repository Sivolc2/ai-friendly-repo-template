# Rules of Change

## Core Principles

### R1: Module Independence
- Each module must be independently deployable
- Modules should communicate through well-defined interfaces
- Avoid direct dependencies between modules

### R2: Interface Stability
- Public APIs must be versioned
- Breaking changes require a new version
- Deprecated features must be marked and documented

### R3: Testing Requirements
- All new features must include unit tests
- Integration tests required for cross-module changes
- Performance tests for critical paths

### R4: Documentation
- All public APIs must be documented
- Architecture changes require ADR
- README files must be kept up to date

### R5: Code Quality
- Follow SOLID principles
- Maximum file size: 500 lines
- Maximum function size: 50 lines
- Use TypeScript strict mode
