# Pipelines (Orchestration Layers)

This directory contains orchestration layers, often referred to as "pipelines" or "use cases." These modules are responsible for coordinating calls to pure functions (from `../functions/`) and adapters (from `../adapters/`) to implement specific application features or business processes.

## Purpose of Pipelines

- **Orchestrate Logic**: Combine multiple pure functions to achieve a larger piece of functionality.
- **Manage Side Effects**: Interact with adapters to perform I/O operations (e.g., fetching data from a database, calling an external API) before or after processing by pure functions.
- **Encapsulate Use Cases**: Each pipeline often represents a single user story or a distinct application feature.
- **Error Handling**: Implement higher-level error handling and data transformation specific to the use case.

## Structure of a Pipeline

A typical pipeline function might:
1. Receive input data (often validated by Pydantic schemas from `../data/`).
2. Call one or more adapter functions to fetch necessary data or perform initial side effects.
3. Pass data to one or more pure functions from `../functions/` for core business logic processing.
4. Call adapter functions again to persist results or trigger further side effects.
5. Return a result (often a Pydantic schema).

## Example (Conceptual)

```python
# In repo_src/backend/pipelines/user_processing.py
from ..functions import data_validation, data_transformation
from ..adapters import user_database_adapter
from ..data import user_schemas

def process_new_user_pipeline(user_data: user_schemas.UserCreate) -> user_schemas.User:
    validated_data = data_validation.validate_user_properties(user_data)
    # ... more pure function calls ...
    created_user_db = user_database_adapter.create_user_in_db(validated_data)
    # ... transform db model to response schema if necessary ...
    return user_schemas.User.from_orm(created_user_db)
```

## Testing Pipelines

Pipeline tests are typically integration tests. They verify that the pipeline correctly orchestrates its constituent functions and adapters. Adapters are often mocked or stubbed during these tests to isolate the pipeline's logic.
