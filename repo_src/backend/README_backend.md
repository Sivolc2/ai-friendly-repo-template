# Backend Documentation

This backend implements a functional-core architecture using FastAPI and SQLAlchemy. It follows SOLID principles and provides a clean separation between pure functions and side effects.

## Architecture

The backend is structured into several key components:

- **Database**: SQLAlchemy models and session management
- **Data**: Pydantic schemas for data validation and serialization
- **Functions**: Pure functions for business logic
- **Pipelines**: Orchestration of pure functions and side effects
- **Adapters**: Database CRUD operations and other side effects

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

3. Run the development server:
```bash
uvicorn repo_src.backend.main:app --reload
```

The API will be available at http://localhost:8000

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

1. Add new pure functions in `functions/`
2. Create or update schemas in `data/`
3. Implement database models in `database/`
4. Add CRUD operations in `adapters/`
5. Create pipelines to orchestrate the flow
6. Add API endpoints in `main.py`
7. Write tests for all new functionality 