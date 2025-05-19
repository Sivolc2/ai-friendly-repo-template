from repo_src.backend.database.connection import engine, Base
# Import all models here so Base has them registered
from repo_src.backend.database import models # noqa Ensures models.py is loaded and Item model is registered with Base

def init_db():
    """
    Initializes the database by creating all tables defined in the models
    that inherit from Base. This is typically called on application startup.
    In a production environment with an existing database, migrations (e.g., Alembic)
    would be used instead of directly calling create_all().
    """
    print(f"Initializing database at {engine.url} and creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created.")

def drop_db():
    """
    Drops all tables from the database. Use with caution, primarily for testing
    or resetting the development environment.
    """
    print(f"Dropping all tables from the database at {engine.url}...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")

if __name__ == "__main__":
    # This allows running `python -m repo_src.backend.database.setup` (from project root)
    # or `python -m backend.database.setup` (from repo_src)
    # Consider adding command line arguments for init/drop actions.
    print("Running database setup script...")
    init_db() # Example: Initialize DB by default if script is run directly. 