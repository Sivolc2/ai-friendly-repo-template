from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

# Default to an in-memory SQLite database if DATABASE_URL is not set,
# good for quick starts or some test scenarios outside of full test suite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app_default.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if ":memory:" in DATABASE_URL: # Specific setup for in-memory SQLite for testing outside of TestClient
        # This StaticPool is more for when you want a single in-memory DB shared across direct test calls.
        # For TestClient, overriding dependencies with a fresh in-memory DB per test is often preferred.
        # engine = create_engine(DATABASE_URL, connect_args=connect_args, poolclass=StaticPool)
        pass # Handled by test_database.py for specific test engine config

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 