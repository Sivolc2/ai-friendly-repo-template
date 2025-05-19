import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession # Renamed to avoid conflict
from sqlalchemy.pool import StaticPool
from typing import Generator

# Use absolute imports for proper pytest resolution
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from repo_src.backend.database.connection import Base, get_db
from repo_src.backend.database.models import Item # Import your models
from repo_src.backend.main import app 

from fastapi.testclient import TestClient

# Use an in-memory SQLite database for testing
DATABASE_URL_TEST = "sqlite:///:memory:"

engine_test = create_engine(
    DATABASE_URL_TEST,
    connect_args={"check_same_thread": False}, # Specific to SQLite
    poolclass=StaticPool, # Use StaticPool for in-memory SQLite with TestClient for a single connection per test
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="function")
def db_session_func() -> Generator[SQLAlchemySession, None, None]:
    """
    Pytest fixture to create a new database session for each test function.
    It creates all tables before the test and drops them afterwards.
    """
    Base.metadata.create_all(bind=engine_test) # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test) # Drop tables after test

# Override the get_db dependency for testing FastAPI endpoints
def override_get_db_for_tests():
    """
    Overrides the get_db dependency in FastAPI to use the test database.
    Ensures tables are created before yielding the session and dropped after.
    This is crucial for TestClient tests that interact with the database.
    """
    Base.metadata.create_all(bind=engine_test) # Ensure tables are created for this test session scope
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test) # Clean up: drop tables

app.dependency_overrides[get_db] = override_get_db_for_tests

client = TestClient(app) # TestClient that uses the overridden get_db

def test_create_item_in_db(db_session_func: SQLAlchemySession):
    # Direct database interaction test using the db_session_func fixture
    new_item = Item(name="Test Item Direct", description="This is a test item created directly.")
    db_session_func.add(new_item)
    db_session_func.commit()
    db_session_func.refresh(new_item)

    assert new_item.id is not None
    assert new_item.name == "Test Item Direct"

    retrieved_item = db_session_func.query(Item).filter(Item.id == new_item.id).first()
    assert retrieved_item is not None
    assert retrieved_item.name == "Test Item Direct"

def test_read_root_endpoint():
    response = client.get("/") # Uses TestClient with overridden DB
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Backend API. Database is initialized."} 