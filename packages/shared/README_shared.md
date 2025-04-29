# Shared

This directory contains shared code, types, and utilities that are used by both the frontend and backend.

## Purpose

The shared package serves as a single source of truth for:

1. **Type Definitions**: Ensuring frontend and backend use the same data structures
2. **API Contracts**: OpenAPI/Swagger definitions, request/response schemas
3. **Constants**: Shared constants, enums, and configuration values
4. **Utilities**: Common utility functions used by both frontend and backend

## Directory Structure

```
├── api/        # Generated OpenAPI definitions
├── constants/  # Shared constants and enums
├── types/      # TypeScript type definitions
└── utils/      # Shared utility functions
```

## Type Generation

Types are generated from backend models using tools like OpenAPI Generator. This ensures that frontend types always match backend types.

### Process

1. Backend defines data models in Pydantic
2. FastAPI generates OpenAPI spec from these models
3. OpenAPI Generator creates TypeScript types from the spec
4. Frontend imports and uses these generated types

## Example Generated Type

```typescript
/**
 * User model
 * @export
 * @interface User
 */
export interface User {
  /**
   * Unique identifier for the user
   * @type {string}
   * @memberof User
   */
  id: string;
  
  /**
   * Full name of the user
   * @type {string}
   * @memberof User
   */
  name: string;
  
  /**
   * Email address of the user
   * @type {string}
   * @memberof User
   */
  email: string;
  
  /**
   * Creation timestamp
   * @type {string}
   * @memberof User
   * @format date-time
   */
  created_at: string;
  
  /**
   * Whether the user is active
   * @type {boolean}
   * @memberof User
   */
  is_active: boolean;
  
  /**
   * User roles
   * @type {Array<string>}
   * @memberof User
   */
  roles: Array<string>;
  
  /**
   * Additional metadata
   * @type {{ [key: string]: any; }}
   * @memberof User
   */
  metadata?: { [key: string]: any; };
}
```

## Usage Guidelines

1. **Only use generated types** from the shared package in the frontend
2. **Never manually edit** the generated files
3. **Keep shared utilities minimal** and focused on common needs
4. **Regenerate types** when backend models change

## CI/CD

The CI pipeline ensures that types are always in sync:

1. Backend changes trigger type regeneration
2. Tests verify that generated types match backend models
3. Frontend tests ensure compatibility with generated types

## Design Differences

- Generated types replace manual type definitions
- API contracts are enforced at compile time
- Constants are shared to ensure consistency
- Shared utils reduce code duplication 