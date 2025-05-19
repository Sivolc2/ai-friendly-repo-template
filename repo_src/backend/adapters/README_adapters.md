# Adapters

This directory contains wrappers for side effects, such as:

- Database interactions (e.g., CRUD operations using SQLAlchemy models from `repo_src/backend/database/models.py` and sessions from `repo_src/backend/database/connection.py`).
- HTTP client calls to external services.
- File system operations.

Adapters should encapsulate the details of I/O, allowing the core business logic (functions, pipelines) to remain pure and testable.
They act as the bridge between your application's pure core and the impure outside world.

Example: An adapter might provide a `get_user_by_id(user_id: int) -> User` function that internally queries the database.
