
## Action 4: Solidify Functional Programming Paradigm & Adapters

*Goal: Make the functional core approach explicit and easy to follow, aiding AI reasoning, code generation, and testability.*

**1. Examples:**
The "Golden Path" implementation in Action 1 already provides these examples:
*   **Pure Function & Test:**
    *   `repo_src/backend/functions/item_utils.py` (e.g., `validate_item_name`, `process_item_description`).
    *   (Tests for these will be added in Action 6).
*   **Pipeline:**
    *   `repo_src/backend/pipelines/item_creation_pipeline.py` (e.g., `create_new_item_pipeline`).
*   **Adapter:**
    *   `repo_src/backend/adapters/crud_items.py` (e.g., `create_db_item`, `get_item`).

**2. Update `README_backend.md` with clear definitions:**
This was also covered in the conceptual diff for `README_backend.md` in Action 2 (see "Core Principles for Adding Code" and "How to Add a New Feature" sections). It clearly delineates the roles of `functions/`, `pipelines/`, `adapters/`, and `main.py`.

**Explanation for Action 4:**
Solidifying the functional programming paradigm with a clear distinction for adapters is key for Software 3.0:
*   **AI Reasoning:** Pure functions are easier for AI to understand, analyze, and generate because their behavior is determined solely by their inputs, without hidden side effects or reliance on external state.
*   **Testability:** Pure functions are trivial to unit test. Pipelines can be tested by mocking adapters. This robust testability allows AI-generated code to be verified more easily.
*   **Modularity & Reusability:** Pure functions are inherently modular and reusable. AI can be prompted to find or create such functions for specific tasks.
*   **Maintainability:** Changes to I/O (e.g., switching a database, modifying an external API call) are isolated to adapters, leaving the core business logic in functions and pipelines untouched. This targeted modification is easier for AI to perform correctly.
*   **Predictable AI Output:** When AI is instructed to generate a "pure function for X" or "an adapter for Y," the constraints of these patterns lead to more predictable and correct code.

The documentation in `README_backend.md` now serves as a "contract" or "style guide" for how code should be structured, which can be fed to AI assistants to guide their code generation.

## Action 6: Bolster Testing Framework

*Goal: Ensure testing is integral, easy, and comprehensive, with working examples that AI can learn from and that CI can validate.*

**1. Populate `repo_src/backend/tests/test_sample.py`**
This file will now contain tests for the new backend logic. Let's rename it to reflect what it's testing, e.g., `test_items.py`.

*   **`repo_src/backend/tests/test_items.py`** (New/Renamed file)
    ```python
    import pytest
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from fastapi.testclient import TestClient

    from repo_src.backend.main import app, get_db as app_get_db # get_db from main.py
    from repo_src.backend.database.session import Base, get_db as original_get_db # original get_db
    from repo_src.backend.database.models import Item as DBItemModel
    from repo_src.backend.data.schemas import ItemCreate, Item as ItemSchema
    from repo_src.backend.functions.item_utils import validate_item_name, process_item_description
    from repo_src.backend.pipelines.item_creation_pipeline import create_new_item_pipeline, ItemCreationError
    from repo_src.backend.adapters.crud_items import create_db_item, get_item, get_items

    # Setup for in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Override the get_db dependency for testing
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[app_get_db] = override_get_db # Use get_db from main.py for override key
    client = TestClient(app)

    @pytest.fixture(scope="function", autouse=True)
    def setup_database():
        # Create tables for each test function
        Base.metadata.create_all(bind=engine)
        yield
        # Drop tables after each test function
        Base.metadata.drop_all(bind=engine)

    # --- Unit Tests for Pure Functions ---
    def test_validate_item_name_valid():
        assert validate_item_name("Valid Name") == True

    def test_validate_item_name_empty():
        assert validate_item_name("") == False
        assert validate_item_name("   ") == False

    def test_validate_item_name_too_long():
        assert validate_item_name("a" * 101) == False

    def test_process_item_description_provided():
        assert process_item_description("  Description  ") == "Description"

    def test_process_item_description_empty():
        assert process_item_description(None) == "No description provided."
        assert process_item_description("") == "No description provided."
        assert process_item_description("   ") == "No description provided."

    # --- Integration Tests for Pipelines (mocking or using test DB) ---
    def test_create_new_item_pipeline_success(setup_database): # Ensure fixture is used
        db: Session = next(override_get_db()) # Get a session for direct pipeline test
        item_data = ItemCreate(name="Test Item", description="A test description")
        created_item = create_new_item_pipeline(item_data=item_data, db=db)
        assert created_item is not None
        assert created_item.name == "Test Item"
        assert created_item.description == "A test description"
        
        # Verify in DB
        db_item_from_db = db.query(DBItemModel).filter(DBItemModel.id == created_item.id).first()
        assert db_item_from_db is not None
        assert db_item_from_db.name == "Test Item"
        db.close()


    def test_create_new_item_pipeline_invalid_name(setup_database):
        db: Session = next(override_get_db())
        item_data = ItemCreate(name="", description="A test description")
        with pytest.raises(ItemCreationError, match="Invalid item name."):
            create_new_item_pipeline(item_data=item_data, db=db)
        db.close()

    # --- API Endpoint Tests (Integration) ---
    def test_create_item_endpoint_success(setup_database):
        response = client.post(
            "/api/v1/items/",
            json={"name": "API Test Item", "description": "Via API"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "API Test Item"
        assert data["description"] == "Via API"
        assert "id" in data

    def test_create_item_endpoint_invalid_name(setup_database):
        response = client.post(
            "/api/v1/items/",
            json={"name": "", "description": "Via API Invalid"},
        )
        assert response.status_code == 400
        assert "Invalid item name." in response.json()["detail"]
        
    def test_read_items_endpoint_empty(setup_database):
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        assert response.json() == []

    def test_read_items_endpoint_with_data(setup_database):
        # Create an item first
        client.post("/api/v1/items/", json={"name": "Item 1", "description": "First Item"})
        client.post("/api/v1/items/", json={"name": "Item 2", "description": "Second Item"})
        
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Item 1"
        assert data[1]["name"] == "Item 2"

    def test_read_single_item_endpoint_found(setup_database):
        create_response = client.post("/api/v1/items/", json={"name": "Specific Item", "description": "Details"})
        item_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Specific Item"
        assert data["id"] == item_id

    def test_read_single_item_endpoint_not_found(setup_database):
        response = client.get("/api/v1/items/999") # Non-existent ID
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"
    ```
    **Explanation:**
    *   Sets up an in-memory SQLite database (`test.db`) specifically for testing.
    *   Uses `FastAPI.TestClient` for testing API endpoints.
    *   `override_get_db` ensures API endpoints use the test database.
    *   The `setup_database` fixture creates and drops tables for each test function, ensuring test isolation.
    *   Includes:
        *   **Unit tests** for pure functions in `item_utils.py`.
        *   **Integration tests** for the `item_creation_pipeline.py`, interacting with the test database.
        *   **API tests** for the FastAPI endpoints, covering success and error cases.

**2. Populate `repo_src/frontend/src/utils/__tests__/sample.test.ts`**
Let's rename this to `ItemsPage.test.tsx` to test the `ItemsPage` component.

*   **`repo_src/frontend/src/pages/__tests__/ItemsPage.test.tsx`** (New/Renamed file, assuming Vitest setup)
    ```tsx
    import React from 'react';
    import { render, screen, fireEvent, waitFor } from '@testing-library/react';
    import '@testing-library/jest-dom'; // For extended matchers
    import ItemsPage from '../ItemsPage';
    import * as api from '../../services/api'; // To mock api calls

    // Mock the api module
    vi.mock('../../services/api');
    const mockedGetItems = vi.mocked(api.getItems);
    const mockedCreateItem = vi.mocked(api.createItem);

    describe('ItemsPage', () => {
      beforeEach(() => {
        // Reset mocks before each test
        mockedGetItems.mockReset();
        mockedCreateItem.mockReset();
      });

      test('renders loading state initially', () => {
        mockedGetItems.mockResolvedValueOnce([]); // Mock a pending promise
        render(<ItemsPage />);
        expect(screen.getByText(/Loading items.../i)).toBeInTheDocument();
      });

      test('fetches and displays items successfully', async () => {
        const mockItems = [
          { id: 1, name: 'Item A', description: 'Description A' },
          { id: 2, name: 'Item B', description: 'Description B' },
        ];
        mockedGetItems.mockResolvedValueOnce(mockItems);

        render(<ItemsPage />);

        await waitFor(() => {
          expect(screen.getByText(/Item A/i)).toBeInTheDocument();
          expect(screen.getByText(/Description A/i)).toBeInTheDocument();
          expect(screen.getByText(/Item B/i)).toBeInTheDocument();
          expect(screen.getByText(/Description B/i)).toBeInTheDocument();
        });
        expect(mockedGetItems).toHaveBeenCalledTimes(1);
      });

      test('displays error message if fetching items fails', async () => {
        mockedGetItems.mockRejectedValueOnce(new Error('Failed to fetch'));
        render(<ItemsPage />);

        await waitFor(() => {
          expect(screen.getByText(/Error: Failed to fetch/i)).toBeInTheDocument();
        });
      });
      
      test('allows creating a new item', async () => {
        mockedGetItems.mockResolvedValueOnce([]); // Initial load
        const newItem = { id: 3, name: 'New Item C', description: 'Freshly created' };
        mockedCreateItem.mockResolvedValueOnce(newItem);

        render(<ItemsPage />);
        
        // Wait for initial load to complete to avoid race conditions
        await waitFor(() => expect(screen.queryByText(/Loading items.../i)).not.toBeInTheDocument());

        fireEvent.change(screen.getByLabelText(/Name:/i), { target: { value: 'New Item C' } });
        fireEvent.change(screen.getByLabelText(/Description:/i), { target: { value: 'Freshly created' } });
        fireEvent.click(screen.getByRole('button', { name: /Create Item/i }));

        await waitFor(() => {
          expect(mockedCreateItem).toHaveBeenCalledWith({
            name: 'New Item C',
            description: 'Freshly created',
          });
          expect(screen.getByText(/New Item C/i)).toBeInTheDocument();
          expect(screen.getByText(/Freshly created/i)).toBeInTheDocument();
        });

        // Check if input fields are cleared
        expect(screen.getByLabelText(/Name:/i)).toHaveValue('');
        expect(screen.getByLabelText(/Description:/i)).toHaveValue('');
      });

       test('displays error message if creating item fails', async () => {
        mockedGetItems.mockResolvedValueOnce([]);
        mockedCreateItem.mockRejectedValueOnce(new Error('Creation failed'));

        render(<ItemsPage />);
        await waitFor(() => expect(screen.queryByText(/Loading items.../i)).not.toBeInTheDocument());


        fireEvent.change(screen.getByLabelText(/Name:/i), { target: { value: 'Fail Item' } });
        fireEvent.click(screen.getByRole('button', { name: /Create Item/i }));

        await waitFor(() => {
          expect(screen.getByText(/Error: Creation failed/i)).toBeInTheDocument();
        });
      });
    });
    ```
    **Explanation:**
    *   Uses `@testing-library/react` for rendering components and interacting with them.
    *   Mocks the `services/api.ts` module using `vi.mock` (assuming Vitest is the test runner, which is common with Vite).
    *   Tests various states: loading, successful data display, error handling for fetch, and item creation.
    *   Uses `waitFor` to handle asynchronous operations.

**3. CI Integration:**
The existing `.github/workflows/ci.yml` already has steps for `pnpm test` (which should run backend tests via `nox` and frontend tests via its `package.json` script).
The key is that `repo_src/backend/package.json`'s `test` script (`nox -s tests`) and `repo_src/frontend/package.json`'s `test` script (e.g., `vitest run`) are correctly configured and these new test files are picked up.

Backend `package.json` has `nox -s tests`. `noxfile.py` runs `pytest`. This setup should pick up `test_items.py`.
Frontend `package.json` is currently empty in the provided context. It needs to be updated for a Vite + React + TS project, including a test script. Assuming a standard Vite setup:

*   **Update `repo_src/frontend/package.json`** (Example content, needs to be the actual one from `pnpm dlx create-vite frontend -- --template react-ts`)
    ```json
    {
      "name": "@workspace/frontend",
      "private": true,
      "version": "0.0.0",
      "type": "module",
      "scripts": {
        "dev": "vite",
        "build": "tsc && vite build",
        "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
        "preview": "vite preview",
        "test": "vitest run",
        "test:ui": "vitest --ui",
        "coverage": "vitest run --coverage"
      },
      "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0"
      },
      "devDependencies": {
        "@testing-library/jest-dom": "^6.4.2",
        "@testing-library/react": "^14.2.1",
        "@testing-library/user-event": "^14.5.2",
        "@types/react": "^18.2.55",
        "@types/react-dom": "^18.2.19",
        "@typescript-eslint/eslint-plugin": "^6.21.0",
        "@typescript-eslint/parser": "^6.21.0",
        "@vitejs/plugin-react": "^4.2.1",
        "eslint": "^8.56.0",
        "eslint-plugin-react-hooks": "^4.6.0",
        "eslint-plugin-react-refresh": "^0.4.5",
        "jsdom": "^24.0.0",
        "typescript": "^5.2.2",
        "vite": "^5.1.0",
        "vitest": "^1.2.2"
      }
    }
    ```
    **Note:** Ensure you have `jsdom` and testing library dependencies for Vitest if they weren't added by default. Update Vitest config (`vite.config.ts` or a separate `vitest.config.ts`) if needed to set up the testing environment (e.g., `globals: true, environment: 'jsdom'`).

**4. Test Environment Variables in `README.testing.md`**
```diff
--- a/README.testing.md
+++ b/README.testing.md
@@ -22,6 +22,11 @@
 ```
 
 Make any necessary adjustments to the `.env` files for your local development environment.
+
+### Test-Specific Environment
+
+*   **Backend:** The `pytest` setup in `repo_src/backend/tests/test_items.py` uses an in-memory SQLite database (`test.db`) and overrides the database session dependency. It does not rely on external `.env` variables for its core database testing. If other integration tests need specific variables, they should be mockable or use defaults.
+*   **Frontend:** Frontend tests (Vitest) will use environment variables defined in `.env.test` or `.env.development` if loaded by Vite/Vitest. For API mocking, as shown in `ItemsPage.test.tsx`, explicit mocking is preferred over live API calls during unit/component tests.
 
 ## Running Tests
 

```

**Explanation for Action 6:**
A robust testing framework is vital for a Software 3.0 approach:
*   **Verification of AI-Generated Code:** Tests provide an automated way to check if AI-generated or modified code meets requirements and doesn't break existing functionality. This is crucial for trusting AI contributions.
*   **Safety Net for Iteration:** As AI and humans iterate on code, a strong test suite catches regressions quickly.
*   **Executable Specifications:** Tests act as a form of executable specification. AI can be prompted to write code that passes these tests.
*   **Pattern Learning for AI:** Well-written tests (like those for pure functions, or component tests with mocked services) provide clear examples for AI to learn from when asked to generate new tests.
*   **CI/CD Enablement:** Automated tests are fundamental for reliable CI/CD pipelines, allowing for faster and safer deployments, even with AI contributing to the codebase.

The provided examples demonstrate unit testing (pure functions), component testing with mocking (frontend), and integration testing (backend pipeline and API endpoints with a test database).
