import nox

# Ensure nox uses the python from the current venv if one is active
nox.options.sessions = ["tests"]
nox.options.reuse_existing_virtualenvs = True 

@nox.session(python=["3.11"]) # Specify Python versions you support
def tests(session):
    session.install("-r", "requirements.txt")  # Install runtime dependencies
    session.install("pytest", "pytest-cov", "pytest-asyncio", "httpx") # Install test dependencies
    session.run("pytest", "-q", "--cov=.", "--cov-report=xml", "--cov-report=term-missing") # Run tests from backend dir 