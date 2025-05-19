# Pure Functions

This directory contains the functional core of the backend application. All modules and functions within this directory should adhere to the principles of pure functions:

1.  **Deterministic**: Given the same input, they always return the same output.
2.  **No Side Effects**: They do not modify any state outside their own scope. This means no I/O operations (database, network, file system), no modification of global variables, and no changes to input arguments if they are mutable.

## Guidelines for Writing Pure Functions

- **Input Types**: Clearly define input types using Python type hints.
- **Output Types**: Clearly define output types using Python type hints.
- **No Print Statements**: Avoid `print()` statements for debugging; use logging in adapter layers if necessary, or return values that can be inspected.
- **Docstrings**: Provide clear docstrings explaining what the function does, its parameters, and what it returns. Follow a consistent docstring format (e.g., Google, NumPy, or reStructuredText).
- **Testability**: Pure functions are inherently easy to test. Ensure comprehensive unit tests for all functions in the `repo_src/backend/tests/functions/` directory (or similar structure).

By keeping business logic in pure functions, the application becomes more predictable, easier to reason about, and simpler to test. Orchestration of these functions and handling of side effects are managed by `pipelines/` and `adapters/` respectively.
