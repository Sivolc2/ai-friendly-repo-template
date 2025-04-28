# Rules for Editing Shared Code

## Overview
This document outlines the rules and processes for modifying shared code in the Collective Creation Engine. Shared code includes:
- `core/` - Core functionality used across the system
- `adapters/` - External service integrations
- `shared-lib/` - Shared utilities and components

## Mandatory Artefacts

### 1. Shared README_{folder_name}.md
- Location: `core/README_core.md`, `adapters/README_adapters.md`, etc.
- Purpose: Document the purpose, architecture, and public API of each module
- Required sections:
  - Overview
  - Architecture
  - Public API
  - Implementation Details

### 2. System Diagram Update
- Location: `docs/01_architecture_overview.mmd`
- Updated by: `pnpm update:diagram`
- Must reflect all shared code dependencies
- Generated from registry data

### 3. Architecture Decision Record (ADR)
- Location: `docs/adr/NNN_<topic>.md`
- Written by: Author of the change
- Required for all shared code modifications
- Must be linked in PR

## Workflow for Shared Code Changes

### 1. Design Phase
1. Read `docs/02_rules_of_change.md` → "Shared edits" section
2. Draft ADR before writing code
3. Get initial review of ADR

### 2. Implementation Phase
1. Make changes in shared package
2. Update affected slices minimally
3. Update documentation:
   ```bash
   pnpm gen:context           # updates every slice & shared READMEs
   pnpm update:diagram        # updates system diagram
   ```

### 3. Pull Request Requirements
PR must include:
- Link to ADR file
- Confirmation of `gen:context` & diagram updates
- List of affected slices
- Stability badge updates if needed

### 4. Review Process
- Human reviewer must mark ADR as "Accepted"
- CI verifies README blocks and diagram presence
- All affected slices must be tested

## Shared README Standards

### Required Sections
```markdown
<!-- INTENT: <purpose>
Owned by: <team/individual>
Stability: <Stable|Experimental|Internal>
-->

<!-- FILE INDEX: auto-generated -->

<!-- PUBLIC API: auto-generated -->
```

### Stability Levels
- **Stable**: Production-ready, backward-compatible
- **Experimental**: New features, may change
- **Internal**: Implementation details, not for external use

## Diagram Updater
The system diagram is automatically updated based on the registry data. The updater:
1. Reads `registry/project_registry.json`
2. Analyzes dependencies between modules
3. Generates Mermaid diagram
4. Updates `docs/01_architecture_overview.mmd`

## Best Practices
1. Keep shared code minimal and focused
2. Document all public APIs
3. Maintain backward compatibility
4. Use type hints and documentation
5. Include comprehensive tests
6. Follow SOLID principles 

## Documentation Standards

### 1. Shared README_{folder_name}.md
- Location: `core/README_core.md`, `adapters/README_adapters.md`, etc.
- Purpose: Document the purpose, architecture, and public API of each module
- Required sections:
  - Overview
  - Architecture
  - Public API
  - Implementation Details

### 2. Code Comments
- Use docstrings for all public functions and classes
- Include type hints in Python code
- Document complex algorithms with inline comments

### 3. Type Definitions
- Define types in separate files (types.py/ts)
- Use dataclasses for Python
- Use TypeScript interfaces for frontend

## Testing Standards

### 1. Unit Tests
- Write tests for all public functions
- Use pytest for backend
- Use Jest for frontend
- Maintain >80% coverage

### 2. Integration Tests
- Test module interactions
- Mock external dependencies
- Use test fixtures

## Code Style

### 1. Python
- Follow PEP 8
- Use black for formatting
- Use isort for imports

### 2. TypeScript
- Follow ESLint rules
- Use Prettier for formatting
- Use strict mode 