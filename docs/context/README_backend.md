# Backend Context

This document provides a high-level overview of the backend architecture and key components.

## Core Principles

1. **Functional Core**: Business logic is implemented as pure functions
2. **Side Effects**: Database and HTTP operations are isolated in adapters
3. **Type Safety**: Comprehensive type hints and validation
4. **SOLID**: Each component has a single responsibility

## Key Components

### Database Layer
- `database/session.py`: SQLAlchemy session management
- `database/models.py`: SQLAlchemy ORM models
- Uses SQLite for simplicity, can be swapped for PostgreSQL

### Data Layer
- `data/schemas.py`: Pydantic models for validation
- Defines clear contracts for API input/output
- Includes field validation and constraints

### Functions Layer
- `functions/item_utils.py`: Pure business logic functions
- No side effects, easily testable
- Handles validation and data processing

### Adapters Layer
- `adapters/crud_items.py`: Database operations
- Isolates side effects from business logic
- Implements CRUD operations

### Pipelines Layer
- `pipelines/item_creation_pipeline.py`: Orchestrates operations
- Combines pure functions and side effects
- Handles error cases and validation

### API Layer
- `main.py`: FastAPI application
- RESTful endpoints for CRUD operations
- Automatic OpenAPI documentation

## Design Patterns

1. **Dependency Injection**: Used for database sessions
2. **Repository Pattern**: CRUD operations in adapters
3. **Pipeline Pattern**: Orchestration of operations
4. **Error Handling**: Custom exceptions and HTTP status codes

## Testing Strategy

1. **Unit Tests**: For pure functions
2. **Integration Tests**: For database operations
3. **API Tests**: For endpoint behavior
4. **Property Tests**: For data validation

## Development Flow

1. Define schemas
2. Implement pure functions
3. Create database models
4. Add CRUD operations
5. Create pipelines
6. Add API endpoints
7. Write tests

## Common Patterns

1. **Validation**: Use Pydantic for input validation
2. **Error Handling**: Custom exceptions with clear messages
3. **Database Operations**: Use SQLAlchemy session context
4. **API Responses**: Consistent response models
5. **Documentation**: Comprehensive docstrings and type hints 