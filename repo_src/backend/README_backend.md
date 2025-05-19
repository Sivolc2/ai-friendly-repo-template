# Backend Documentation

This backend implements a functional-core architecture using FastAPI and SQLAlchemy (with SQLite as the default database). It follows SOLID principles and provides a clean separation between pure functions and side effects.

## Architecture

The backend is structured into several key components:

- **`main.py`**: FastAPI application entrypoint, global configurations, and API routers.
- **`database/`**: SQLAlchemy models, database connection setup (`connection.py`), and table initialization logic (`setup.py`).
- **Data**: Pydantic schemas for data validation and serialization (located in `data/`).
- **Functions**: Pure functions for business logic (located in `functions/`).
- **Pipelines**: Orchestration of pure functions and side effects (located in `pipelines/`).
- **Adapters**: Wrappers for database CRUD operations, external API calls, and other side effects (located in `adapters/`).

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables. Copy `.env.example` to `.env` in this directory and customize if needed:
```bash
cp .env.example .env
```

3. Run the development server:
```bash
uvicorn repo_src.backend.main:app --reload
```

The API will be available at http://localhost:8000

## Database

The backend uses SQLAlchemy for ORM and SQLite as the default database for development and testing.

- **Configuration**: The database URL is configured via the `DATABASE_URL` environment variable (see `.env.example`). Default is `sqlite:///./app.db` (for application) or `sqlite:///./app_dev.db` (from `.env.defaults`).
- **Models**: SQLAlchemy models are defined in `repo_src/backend/database/models.py`.
- **Initialization**: The database and tables are automatically initialized on application startup by `repo_src.backend.database.setup:init_db()`. You can also manually run `python -m repo_src.backend.database.setup init` from the project root to create tables if needed (ensure your `PYTHONPATH` or current working directory is set up correctly for module resolution, or run as `python -m backend.database.setup init` from `repo_src`).
- **Sessions**: Database sessions are managed by `repo_src.backend.database.connection:get_db()`, which can be used as a FastAPI dependency.
- **Migrations**: For this template, migrations are handled by dropping and recreating tables via `Base.metadata.create_all()` and `Base.metadata.drop_all()`. This is suitable for SQLite in development. For production environments or more complex databases (like PostgreSQL), a migration tool like Alembic should be integrated.

To manually initialize the database (e.g., if you added new models and the app isn't running):
```bash
# From the project root directory
python -c "from repo_src.backend.database.setup import init_db; init_db()"
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
pytest
```

## Design Differences

This implementation differs from the guide in several ways:

1. **Enhanced Error Handling**: Added more comprehensive error handling and validation
2. **Search Functionality**: Added search capability to the items list endpoint
3. **Pagination**: Implemented proper pagination with validation
4. **Timestamps**: Added created_at and updated_at fields to track item history
5. **Type Safety**: Enhanced type hints and validation throughout the codebase
6. **Documentation**: Added comprehensive docstrings and API documentation

## Development Flow

1. Define or update Pydantic schemas in `data/`.
2. Define or update SQLAlchemy models in `database/models.py`.
3. Add new pure functions in `functions/`.
4. Implement database interaction logic (CRUD) typically within `adapters/` or directly in endpoints for simple cases, using sessions from `database/connection.py`.
5. Create pipelines in `pipelines/` to orchestrate business logic.
6. Add or update API endpoints in `main.py`, injecting database sessions as dependencies.
7. Write tests for all new functionality, including database interactions (see `tests/test_database.py`).
8. Ensure `python -m repo_src.backend.database.setup init` (or app startup) correctly creates any new tables/columns. For complex changes, plan migration steps using a tool like Alembic for production. 