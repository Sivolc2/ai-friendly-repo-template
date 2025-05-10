## Action 2: Refine Documentation and Guides

*Goal: Make context readily available and understandable for both human developers and AI agents, ensuring clear contribution guidelines.*

**1. Update `repo_src/backend/README_backend.md`**
(Content will be added/modified, this is a conceptual diff)
```diff
--- a/repo_src/backend/README_backend.md
+++ b/repo_src/backend/README_backend.md
@@ -1 +1,80 @@
+# Backend (Python with Functional Core & FastAPI)
+
+This directory contains the Python backend for the application, built with FastAPI and emphasizing a functional core approach.
+
+## Project Structure
+
+├── adapters/      # DB / HTTP side-effect wrappers (e.g., `crud_items.py`)
+├── data/          # Immutable schemas (Pydantic models like `schemas.py`) and constants
+├── database/      # Database setup, SQLAlchemy models (e.g., `models.py`, `session.py`)
+├── functions/     # Pure functions, core business logic (e.g., `item_utils.py`)
+├── pipelines/     # Orchestration layers, composing functions and adapters (e.g., `item_creation_pipeline.py`)
+├── tests/         # Unit and integration tests
+├── utils/         # Generic helpers (if any)
+├── main.py        # FastAPI entrypoint, HTTP routing
+└── README_backend.md
+
+## Core Principles for Adding Code
+
+1.  **Functional Core, Imperative Shell:**
+    *   **`functions/`**: Business logic resides here as pure functions. They take data, process it, and return new data without side effects (no I/O, no external state modification). This makes them easy to test and reason about (for humans and AI).
+    *   **`pipelines/`**: Orchestrate calls to pure functions from `functions/` and adapter functions from `adapters/`. They manage the flow of data and can handle application-specific error states.
+    *   **`adapters/`**: Handle all I/O and interactions with the "outside world" (databases, external APIs, etc.). They translate data between the external world and the internal application's data structures (Pydantic schemas).
+    *   **`main.py` (API Endpoints):** These are the "imperative shell." They handle HTTP requests/responses, use `Depends` for things like DB sessions, call pipelines or adapters, and format responses.
+
+2.  **Clear Data Contracts:**
+    *   Use Pydantic models defined in `repo_src/backend/data/schemas.py` for API request/response bodies and for data passed between layers. This provides strong typing and validation.
+
+3.  **Testing:**
+    *   Write unit tests for all pure functions in `functions/`.
+    *   Write integration tests for pipelines, mocking adapters where necessary.
+    *   API/E2E tests will cover endpoint behavior (see root `README.testing.md`).
+
+## How to Add a New Feature (e.g., a "Product" entity)
+
+1.  **Define Data Schemas (`repo_src/backend/data/schemas.py`):**
+    *   Create Pydantic models for `ProductBase`, `ProductCreate`, `Product` (similar to `Item` schemas).
+    ```python
+    # Example in schemas.py
+    class ProductBase(BaseModel):
+        name: str
+        price: float
+
+    class ProductCreate(ProductBase):
+        pass
+
+    class Product(ProductBase):
+        id: int
+        class Config: orm_mode = True
+    ```
+
+2.  **Define Database Model (`repo_src/backend/database/models.py`):**
+    *   Create a SQLAlchemy model for `Product`. Remember to add `models.Base.metadata.create_all(bind=engine)` in `main.py` if it's not already there or ensure migrations handle it.
+    ```python
+    # Example in models.py
+    class Product(Base):
+        __tablename__ = "products"
+        id = Column(Integer, primary_key=True, index=True)
+        name = Column(String, index=True)
+        price = Column(Float, index=True)
+    ```
+
+3.  **Create Pure Functions (`repo_src/backend/functions/product_utils.py`):**
+    *   Implement any business logic specific to products as pure functions (e.g., `validate_product_price(price: float) -> bool`).
+
+4.  **Create CRUD Adapters (`repo_src/backend/adapters/crud_products.py`):**
+    *   Implement functions to interact with the database for products (e.g., `get_product`, `create_db_product`).
+
+5.  **Create Pipelines (`repo_src/backend/pipelines/product_pipeline.py`):**
+    *   Orchestrate the creation, update, or retrieval logic using functions from `product_utils.py` and adapters from `crud_products.py`.
+
+6.  **Add API Endpoints (`repo_src/backend/main.py`):**
+    *   Define FastAPI routes for your product (e.g., `POST /products`, `GET /products/{product_id}`).
+    *   Use dependency injection for the DB session (`db: Session = Depends(get_db)`).
+    *   Call your product pipelines or CRUD adapters.
+    *   Use the Pydantic schemas for request bodies and response models.
+
+7.  **Write Tests:**
+    *   Unit tests for functions in `product_utils.py`.
+    *   Integration tests for pipelines in `product_pipeline.py`.
+    *   Consider E2E tests for the new API endpoints.
+
+## Local Development
+
+To run the backend server locally:
+```bash
+# Ensure your virtual environment is active
+cd repo_src/backend
+uvicorn main:app --reload --port 8000
+```
+
+The API will be available at `http://localhost:8000`. Swagger UI documentation will be at `http://localhost:8000/docs`.

```

**2. Update `repo_src/frontend/README_frontend.md`**
(Conceptual diff)
```diff
--- a/repo_src/frontend/README_frontend.md
+++ b/repo_src/frontend/README_frontend.md
@@ -1 +1,65 @@
+# Frontend (React with TypeScript + Vite)
+
+This directory contains the React/TypeScript frontend application, built with Vite.
+
+## Project Structure
+
+├── public/            # Static assets directly served
+├── src/
+│   ├── assets/        # Images, fonts, etc., imported by components
+│   ├── components/    # Reusable UI components
+│   ├── hooks/         # Custom React hooks
+│   ├── pages/         # Route-level components (e.g., `ItemsPage.tsx`)
+│   ├── services/      # API clients and other services (e.g., `api.ts`)
+│   ├── styles/        # Global styles, CSS variables, themes
+│   ├── types/         # TypeScript type definitions (e.g., `item.ts`)
+│   ├── utils/         # Utility functions
+│   ├── main.tsx       # Main entry point for React
+│   └── App.tsx        # Root application component
+├── .env.example       # Example environment variables
+├── index.html         # Main HTML file
+├── package.json       # Project dependencies and scripts
+├── tsconfig.json      # TypeScript configuration
+├── vite.config.ts     # Vite configuration
+└── README_frontend.md
+
+## Core Principles for Adding Code
+
+1.  **Component-Based Architecture:** Build UI as a composition of reusable components.
+2.  **Strong Typing:** Leverage TypeScript for type safety and improved developer experience (and AI understanding). Define types for props, state, API responses in `src/types/`.
+3.  **Separation of Concerns:**
+    *   **`components/`**: Dumb/presentational components if possible.
+    *   **`pages/`**: Container components that manage state and data fetching for a view.
+    *   **`hooks/`**: Reusable stateful logic.
+    *   **`services/`**: Logic for API calls and other external interactions.
+4.  **Styling:**
+    *   A global stylesheet can be placed in `src/styles/global.css` (or similar) and imported in `main.tsx`.
+    *   For component-specific styles, consider CSS Modules or a CSS-in-JS solution if preferred. (Currently, no specific library is enforced; basic global CSS is assumed for simplicity).
+
+## How to Add a New Feature (e.g., a "Products" page)
+
+1.  **Define Types (`src/types/product.ts`):**
+    *   Create a TypeScript interface for `Product` data, matching the backend schema.
+
+2.  **Create API Service (`src/services/productApi.ts` or add to `api.ts`):**
+    *   Add functions to fetch/create/update product data from the backend.
+
+3.  **Create Components (`src/components/ProductCard.tsx`, etc.):**
+    *   Develop any reusable components needed to display product information.
+
+4.  **Create Page Component (`src/pages/ProductsPage.tsx`):**
+    *   This component will:
+        *   Use the API service to fetch product data.
+        *   Manage state for products, loading, and errors.
+        *   Render the list of products, possibly using `ProductCard` components.
+        *   Handle user interactions (e.g., form for adding a new product).
+
+5.  **Add Routing (if applicable, e.g., in `App.tsx` with `react-router-dom`):**
+    *   If you're using a router, add a route for `/products` that renders `ProductsPage`. (Currently, `App.tsx` is simple and doesn't use a router).
+
+6.  **Write Tests:**
+    *   Write unit/integration tests for new components and hooks using Vitest and React Testing Library.
+
+## Local Development
+
+To run the frontend development server:
+```bash
+# From the project root
+pnpm dev:frontend
+```
+The application will typically be available at `http://localhost:5173`.

```

**3. Review other `README_{folder_name}.md` files**
For brevity, I won't list all of them, but the principle is:
*   Each `README_{folder_name}.md` (e.g., `repo_src/backend/functions/README_functions.md`) should clearly state:
    1.  The precise purpose of the folder.
    2.  Strict rules/conditions for adding code (e.g., "Functions in this folder MUST be pure," "Pipelines MUST NOT contain direct DB calls but use adapters").
    3.  Expected inputs/outputs or interaction patterns.
    4.  Links to relevant architectural patterns or examples.

**4. Create/Fix `repo_src/scripts/export_context.py`**
The existing script from `docs/-1_starter_doc.md` is a good starting point but needs modification to output to the `registry/` directory and generate the specified markdown files.

```python
#!/usr/bin/env python
"""
Walks backend & frontend directories and emits:
  registry/backend_context.md    – human-readable summary of backend
  registry/frontend_context.md   – human-readable summary of frontend
  registry/pipeline_context.md   – human-readable summary of pipelines
  registry/context.json          – machine-readable for LLM prompts (function/component list)
"""
import ast
import json
import hashlib
import textwrap
import pathlib
import os

ROOT = pathlib.Path(__file__).resolve().parents[2] # Project root
BACKEND_SRC = ROOT / "repo_src" / "backend"
FRONTEND_SRC = ROOT / "repo_src" / "frontend" / "src"
REGISTRY_DIR = ROOT / "registry"

def ensure_registry_dir():
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

def parse_python_file(py_file_path):
    """Parses a Python file and extracts function information."""
    functions = []
    try:
        with open(py_file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        node = ast.parse(source)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                docstring = ast.get_docstring(item) or "No docstring."
                functions.append({
                    "type": "function",
                    "file": str(py_file_path.relative_to(ROOT)),
                    "name": item.name,
                    "args": [a.arg for a in item.args.args],
                    "doc": docstring.split("\n")[0].strip(),  # First line of docstring
                    "hash": hashlib.md5(ast.unparse(item).encode()).hexdigest()[:8]
                })
    except Exception as e:
        print(f"Error parsing Python file {py_file_path}: {e}")
    return functions

def parse_typescript_file(ts_file_path):
    """Rudimentary parsing for TS/TSX files to find exported functions/components."""
    # This is a very basic parser. A more robust solution would use a TS parser library.
    components = []
    try:
        with open(ts_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for exported functions or consts (potential components)
        # Example: export const MyComponent = (...) => { ... }
        # Example: export function MyFunction(...) { ... }
        # This regex is basic and might need refinement for complex cases.
        import re
        # Regex to find exported functions, consts (React components), and interfaces/types
        pattern = re.compile(
            r"export\s+(?:const|let|var|function|class|interface|type)\s+([A-Za-z_][A-Za-z0-9_]*)"
        )
        found_names = set() # Avoid duplicates if multiple export styles are used for same item

        for match in pattern.finditer(content):
            name = match.group(1)
            if name not in found_names:
                components.append({
                    "type": "component_or_function_or_type", # General type for frontend
                    "file": str(ts_file_path.relative_to(ROOT)),
                    "name": name,
                    "doc": "TS/TSX item. Docstring extraction needs more advanced parsing.",
                })
                found_names.add(name)

    except Exception as e:
        print(f"Error parsing TS/TSX file {ts_file_path}: {e}")
    return components


def generate_backend_context(all_funcs):
    """Generates backend_context.md"""
    content = ["# Backend Context", "\nA concise index of backend functionality.\n"]
    
    # Group by directory
    files_by_dir = {}
    for func_info in all_funcs:
        if not func_info["file"].startswith("repo_src/backend"):
            continue
        
        file_path = pathlib.Path(func_info["file"])
        dir_path = str(file_path.parent)
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(func_info)

    for dir_path, funcs_in_dir in sorted(files_by_dir.items()):
        content.append(f"\n## Directory: `{dir_path}`\n")
        content.append("| Function | Args | Summary |")
        content.append("|---|---|---|")
        for func_info in sorted(funcs_in_dir, key=lambda x: x["name"]):
            args_str = ", ".join(func_info.get("args", []))
            content.append(f"| `{func_info['name']}` | `{args_str}` | {func_info['doc']} |")
    
    with open(REGISTRY_DIR / "backend_context.md", 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    print("Generated registry/backend_context.md")

def generate_frontend_context(all_frontend_items):
    """Generates frontend_context.md"""
    content = ["# Frontend Context", "\nA concise index of frontend components, functions, and types.\n"]

    files_by_dir = {}
    for item_info in all_frontend_items:
        if not item_info["file"].startswith("repo_src/frontend"):
            continue
        
        file_path = pathlib.Path(item_info["file"])
        dir_path = str(file_path.parent)
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(item_info)

    for dir_path, items_in_dir in sorted(files_by_dir.items()):
        content.append(f"\n## Directory: `{dir_path}`\n")
        content.append("| Item Name | Type | File Path |")
        content.append("|---|---|---|")
        for item_info in sorted(items_in_dir, key=lambda x: x["name"]):
            content.append(f"| `{item_info['name']}` | {item_info['type']} | `{item_info['file']}` |")

    with open(REGISTRY_DIR / "frontend_context.md", 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    print("Generated registry/frontend_context.md")


def generate_pipeline_context(all_funcs):
    """Generates pipeline_context.md"""
    content = ["# Pipeline Context", "\nSummary of all pipelines in the application.\n"]
    
    pipeline_funcs = [
        f for f in all_funcs if "pipeline" in f["file"] and f["file"].startswith("repo_src/backend/pipelines")
    ]

    if not pipeline_funcs:
        content.append("No pipeline functions found in `repo_src/backend/pipelines/`.")
    else:
        content.append("## Pipelines\n")
        content.append("This directory contains pipeline orchestrators that compose pure functions to implement features.\n")
        content.append("| Pipeline Function | Args | Summary | File |")
        content.append("|---|---|---|---|")
        for func_info in sorted(pipeline_funcs, key=lambda x: x["name"]):
            args_str = ", ".join(func_info.get("args", []))
            content.append(f"| `{func_info['name']}` | `{args_str}` | {func_info['doc']} | `{func_info['file']}` |")
    
    with open(REGISTRY_DIR / "pipeline_context.md", 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    print("Generated registry/pipeline_context.md")

def main():
    ensure_registry_dir()
    
    all_python_functions = []
    # Backend Python files
    for py_file in BACKEND_SRC.rglob("*.py"):
        if "tests" in py_file.parts or py_file.name.startswith("_") or ".venv" in py_file.parts:
            continue
        all_python_functions.extend(parse_python_file(py_file))

    all_frontend_items = []
    # Frontend TS/TSX files
    for ts_file in FRONTEND_SRC.rglob("*.ts*"): # Handles .ts and .tsx
        if "test" in ts_file.name.lower() or "spec" in ts_file.name.lower() or "node_modules" in ts_file.parts:
            continue
        all_frontend_items.extend(parse_typescript_file(ts_file))

    # Combined context for context.json
    combined_context = all_python_functions + all_frontend_items
    with open(REGISTRY_DIR / "context.json", 'w', encoding='utf-8') as f:
        json.dump(combined_context, f, indent=2)
    print(f"Generated registry/context.json with {len(combined_context)} items.")

    generate_backend_context(all_python_functions)
    generate_frontend_context(all_frontend_items)
    generate_pipeline_context(all_python_functions)
    
    print("Context export complete.")

if __name__ == "__main__":
    main()
```
**Explanation:**
*   The script now targets the `registry/` directory.
*   It has distinct parsing for Python and a rudimentary one for TypeScript (a proper TS AST parser would be much more robust but adds complexity).
*   `generate_backend_context`, `generate_frontend_context`, and `generate_pipeline_context` functions create the respective Markdown files.
*   `context.json` now includes items from both backend and frontend.
*   This script, when run via `pnpm ctx:sync` (or `pnpm registry:update`), will keep the `registry/` up-to-date, providing crucial structured context for AI agents.
*   The CI step `git diff --exit-code registry/` is vital to ensure these context files are committed.

**5. Update `docs/feature_flow.md`**
```diff
--- a/docs/feature_flow.md
+++ b/docs/feature_flow.md
@@ -1,14 +1,32 @@
 # Feature Development Workflow
 
-This document outlines the step-by-step process for developing new features in this repository.
+This document outlines the step-by-step process for developing new features in this repository, emphasizing collaboration with AI assistants.
 
 | Step | Command / action | Output & gate | AI Assistance Notes |
 |------|------------------|---------------|---------------------|
-| **1. Draft PRD** | Create `docs/prd/NNN-<slug>.md` using registry of functions (reuse where possible) + guides | Must list *acceptance criteria* |
-| **2. Red tests** | Author unit tests in `backend/tests/<slug>/` | CI must show failures |
-| **3. Implement** | Write pure functions until tests pass | `pnpm test` ✔ |
-| **4. Compose pipeline** | Add orchestrator in `pipelines/` | Pipeline tests green |
-| **5. Wire adapters** | (If needed) add side-effect impl in `adapters/` | Integration tests green |
-| **6. Sync docs** | `pnpm ctx:sync` | No drift detected |
-| **7. Open PR** | - | CI: lint, type, test, ctx |
-| **8. Merge** | - | Done |
-
+| **1. Understand & Plan** | Review existing `registry/` context, relevant `README_*.md` files. Discuss requirements. | Clear understanding of feature scope and impact. | Use AI to explore existing codebase via `registry/` context to identify reusable components/functions. |
+| **2. Draft PRD** | Create `docs/prd/NNN-<slug>.md`. Use `code_builder/main_orchestrator.sh "feature description"` or manually write PRD. | PRD must list: Goals, User Stories (if any), Detailed Technical Plan (functions, data schemas, pipeline flow, adapters needed), Acceptance Criteria. | AI (via `code_builder`) can generate the initial PRD draft. Human reviews and refines it. |
+| **3. Scaffold Feature** | `pnpm new:feature <slug>` (once script is ready) or manually create directories and stub files. | Stub directories/files for functions, pipelines, tests, components. | AI can generate stub files based on the PRD's technical plan. |
+| **4. Write Tests (TDD approach recommended)** | Author unit tests for pure functions (`repo_src/backend/functions/`, `repo_src/frontend/src/utils/`) and integration tests for pipelines/components. | CI must show initial test failures (Red). | AI can help generate test cases based on function/component specifications in the PRD and acceptance criteria. |
+| **5. Implement Pure Functions & UI Components** | Write code in `repo_src/backend/functions/` and `repo_src/frontend/src/{components,hooks,utils}/`. Ensure tests pass. | `pnpm test` ✔ (Green for unit tests). | AI implements functions/components based on PRD and its understanding of existing patterns from the golden path app. Human reviews and iterates with AI. |
+| **6. Compose Pipeline / Wire UI** | Backend: Add orchestrator in `repo_src/backend/pipelines/`. Frontend: Integrate components into pages, manage state, connect to services. Ensure tests pass. | Pipeline tests green. UI interactions work as expected. | AI helps compose pipelines or wire UI elements, referencing the PRD's flow. |
+| **7. Implement Adapters / API Services** | Backend: (If needed) add side-effect impl in `repo_src/backend/adapters/`. Frontend: Implement calls in `repo_src/frontend/src/services/`. | Integration tests green. API communication works. | AI can generate adapter/service code based on external API contracts or DB schema definitions. |
+| **8. Sync Docs & Registry** | `pnpm ctx:sync` (or `pnpm registry:update`) | No drift detected in `registry/`. | AI (if capable through an agent) could be prompted to update related `README_*.md` docstrings if significant changes were made. Otherwise, human responsibility. |
+| **9. Manual E2E & QA** | Manually test the feature flow. Run E2E tests: `pnpm e2e`. | Feature works as per acceptance criteria. E2E tests pass. | - |
+| **10. Open PR** | Create Pull Request. Describe changes, link to PRD. | - | AI can help summarize changes for the PR description based on commits. |
+| **11. Code Review** | Human team members review the PR. | Code quality, adherence to patterns, correctness. | - |
+| **12. Merge** | Merge PR after approval and passing CI. | CI: lint, type, test, ctx sync. | - |

```
**Explanation for Action 2:**
These documentation updates are crucial for "Software 3.0":
*   **Clear "How-To" Guides:** Reduce cognitive load for human developers and provide structured information that AI can follow to generate code in the correct locations and styles.
*   **Folder Contribution Rules:** Enforce consistency. AI agents, when properly prompted with these rules (e.g., via `alwaysApply` in Cursor or as part of a system prompt), are more likely to adhere to the architectural design.
*   **`export_context.py` and `registry/`:** This is the cornerstone of providing dynamic, accurate, and structured context to AI tools. Instead of relying on large, static context windows, AI can be fed relevant summaries and indices from `registry/`, making its responses more accurate and efficient.
*   **Updated `feature_flow.md`:** Explicitly incorporating AI assistance steps into the workflow guides developers on how to best leverage AI, turning it into a collaborative partner. It also highlights the importance of human oversight (review, PRD refinement).
