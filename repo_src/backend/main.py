from fastapi import FastAPI
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

# Load environment variables from .env file if it exists
# This is particularly useful for local development.
# In production, environment variables should be set through the deployment environment.

# Determine the directory of the current file (main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file relative to main.py
env_path_backend = os.path.join(current_dir, '.env')

# Construct the path to the .env file in the project root (if applicable)
project_root_env = os.path.join(current_dir, '..', '..', '.env') # Assuming repo_src/backend/main.py

if os.path.exists(env_path_backend):
    print(f"Loading environment variables from: {env_path_backend}")
    load_dotenv(dotenv_path=env_path_backend)
elif os.path.exists(project_root_env) and os.path.basename(os.getcwd()) != "backend":
    # Only load project root .env if not already in backend (where local .env takes precedence)
    print(f"Loading environment variables from project root: {project_root_env}")
    load_dotenv(dotenv_path=project_root_env)
else:
    print("No .env file found in backend directory or project root, or backend/.env takes precedence. Relying on system environment variables.")

# Import database setup function AFTER loading env vars,
# as db connection might depend on them.
from .database.setup import init_db
from .database import models, connection # For example endpoints
# from .data import schemas # Assuming you'll have Pydantic schemas in data/

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("Application startup: Initializing database...")
    init_db() # Initialize database and create tables
    print("Application startup complete.")
    yield
    # Shutdown: Clean up resources if needed
    print("Application shutdown: Cleaning up resources...")
    # Any cleanup code would go here
    print("Application shutdown complete.")

app = FastAPI(title="AI-Friendly Repository Backend", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the Backend API. Database is initialized."}

# Example (commented out) CRUD endpoints would go here
# You would typically put these in separate router files (e.g., in an `api` or `routers` directory)
# and include them in the main app.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level=os.getenv("LOG_LEVEL", "info").lower())
