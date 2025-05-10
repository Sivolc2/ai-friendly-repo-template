
## Action 7: Streamline Developer Tooling & Scripts

*Goal: Provide helpful, working scripts for common development tasks, improving developer velocity and consistency, whether for human or AI-driven actions.*

**1. Complete `repo_src/scripts/setup-env.sh`**
```bash
#!/bin/bash

# Copies .env.defaults to the respective frontend and backend .env locations
# if the target .env files do not already exist.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/.." # Adjusted to be project root from repo_src/scripts
DEFAULTS_ENV_FILE="${PROJECT_ROOT}/.env.defaults"

FRONTEND_ENV_DIR="${PROJECT_ROOT}/repo_src/frontend"
FRONTEND_ENV_FILE="${FRONTEND_ENV_DIR}/.env"

BACKEND_ENV_DIR="${PROJECT_ROOT}/repo_src/backend"
BACKEND_ENV_FILE="${BACKEND_ENV_DIR}/.env"

# Check if .env.defaults exists
if [ ! -f "$DEFAULTS_ENV_FILE" ]; then
  echo "Error: Default environment file not found at $DEFAULTS_ENV_FILE"
  exit 1
fi

echo "Setting up environment files..."

# Setup for frontend
if [ ! -f "$FRONTEND_ENV_FILE" ]; then
  cp "$DEFAULTS_ENV_FILE" "$FRONTEND_ENV_FILE"
  echo "Created $FRONTEND_ENV_FILE from defaults."
else
  echo "$FRONTEND_ENV_FILE already exists. Skipping."
fi

# Setup for backend
if [ ! -f "$BACKEND_ENV_FILE" ]; then
  cp "$DEFAULTS_ENV_FILE" "$BACKEND_ENV_FILE"
  echo "Created $BACKEND_ENV_FILE from defaults."
else
  echo "$BACKEND_ENV_FILE already exists. Skipping."
fi

echo "Environment file setup complete."
```
**Explanation:** This script now correctly locates `.env.defaults` at the project root and copies it to `repo_src/frontend/.env` and `repo_src/backend/.env` *only if* those files don't already exist. This prevents accidental overwriting of user-specific configurations.

**2. Implement `repo_src/scripts/scaffold_feature.js` (or Python equivalent)**
Let's implement this as a Python script for consistency with `export_context.py` and because Python is already a core part of the backend.

*   **`repo_src/scripts/scaffold_feature.py`** (New file)
    ```python
    #!/usr/bin/env python3
    import argparse
    import pathlib
    import re

    PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
    BACKEND_ROOT = PROJECT_ROOT / "repo_src" / "backend"
    FRONTEND_ROOT = PROJECT_ROOT / "repo_src" / "frontend" / "src"

    def to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def to_pascal_case(name):
        return "".join(word.capitalize() for word in re.split('_|-', name))

    def scaffold_backend(feature_slug_snake, feature_slug_pascal):
        print(f"\nScaffolding backend for feature: {feature_slug_snake}")

        # Functions
        func_dir = BACKEND_ROOT / "functions"
        func_file = func_dir / f"{feature_slug_snake}_utils.py"
        func_dir.mkdir(parents=True, exist_ok=True)
        if not func_file.exists():
            func_file.write_text(
                f"# Pure functions for {feature_slug_snake} feature\n\n"
                f"def example_{feature_slug_snake}_function(param: str) -> str:\n"
                f"    \"\"\"Example pure function for {feature_slug_pascal}.\"\"\"\n"
                f"    return f\"Processed: {{param}}\"\n"
            )
            print(f"  Created: {func_file}")

        # Adapters (CRUD example)
        adapter_dir = BACKEND_ROOT / "adapters"
        adapter_file = adapter_dir / f"crud_{feature_slug_snake}.py"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        if not adapter_file.exists():
            adapter_file.write_text(
                f"from sqlalchemy.orm import Session\n"
                f"# from ..database import models as db_models # Adjust import based on your models\n"
                f"# from ..data import schemas as pydantic_schemas # Adjust import for schemas\n\n"
                f"def get_{feature_slug_snake}_example(db: Session, item_id: int):\n"
                f"    \"\"\"Example GET operation for {feature_slug_pascal}.\"\"\"\n"
                f"    # return db.query(db_models.{feature_slug_pascal}DB).filter(db_models.{feature_slug_pascal}DB.id == item_id).first()\n"
                f"    pass\n\n"
                f"def create_{feature_slug_snake}_example(db: Session, item_data):\n"
                f"    \"\"\"Example CREATE operation for {feature_slug_pascal}.\"\"\"\n"
                f"    # db_item = db_models.{feature_slug_pascal}DB(**item_data.dict())\n"
                f"    # db.add(db_item)\n"
                f"    # db.commit()\n"
                f"    # db.refresh(db_item)\n"
                f"    # return db_item\n"
                f"    pass\n"
            )
            print(f"  Created: {adapter_file}")

        # Pipelines
        pipeline_dir = BACKEND_ROOT / "pipelines"
        pipeline_file = pipeline_dir / f"{feature_slug_snake}_pipeline.py"
        pipeline_dir.mkdir(parents=True, exist_ok=True)
        if not pipeline_file.exists():
            pipeline_file.write_text(
                f"# Orchestration logic for {feature_slug_snake} feature\n"
                f"from sqlalchemy.orm import Session\n"
                f"# from ..functions.{feature_slug_snake}_utils import example_{feature_slug_snake}_function\n"
                f"# from ..adapters.crud_{feature_slug_snake} import create_{feature_slug_snake}_example\n\n"
                f"def process_{feature_slug_snake}_data_pipeline(data: dict, db: Session):\n"
                f"    \"\"\"Example pipeline for {feature_slug_pascal}.\"\"\"\n"
                f"    # processed_param = example_{feature_slug_snake}_function(data.get('param'))\n"
                f"    # result = create_{feature_slug_snake}_example(db=db, item_data=processed_param)\n"
                f"    # return result\n"
                f"    pass\n"
            )
            print(f"  Created: {pipeline_file}")

        # Tests
        test_dir = BACKEND_ROOT / "tests"
        test_func_file = test_dir / f"test_{feature_slug_snake}_utils.py"
        test_pipeline_file = test_dir / f"test_{feature_slug_snake}_pipeline.py"
        test_dir.mkdir(parents=True, exist_ok=True)
        if not test_func_file.exists():
            test_func_file.write_text(
                f"import pytest\n"
                f"# from ..functions.{feature_slug_snake}_utils import example_{feature_slug_snake}_function\n\n"
                f"def test_example_{feature_slug_snake}_function():\n"
                f"    # assert example_{feature_slug_snake}_function(\"test\") == \"Processed: test\"\n"
                f"    pass\n"
            )
            print(f"  Created: {test_func_file}")
        if not test_pipeline_file.exists():
            test_pipeline_file.write_text(
                f"import pytest\n"
                f"# from ..pipelines.{feature_slug_snake}_pipeline import process_{feature_slug_snake}_data_pipeline\n"
                f"# from unittest.mock import MagicMock\n\n"
                f"def test_process_{feature_slug_snake}_data_pipeline():\n"
                f"    # mock_db_session = MagicMock()\n"
                f"    # result = process_{feature_slug_snake}_data_pipeline({{'param': 'test'}}, db=mock_db_session)\n"
                f"    # assert result is not None # or other assertions\n"
                f"    pass\n"
            )
            print(f"  Created: {test_pipeline_file}")
        
        # Data Schemas (Pydantic)
        schemas_dir = BACKEND_ROOT / "data"
        schemas_file = schemas_dir / "schemas.py" # Assumes one central schemas file for now
        schemas_dir.mkdir(parents=True, exist_ok=True)
        if schemas_file.exists():
             with open(schemas_file, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n# Schemas for {feature_slug_pascal}\n"
                    f"class {feature_slug_pascal}Base(BaseModel):\n"
                    f"    name: str\n"
                    f"    # Add other fields\n\n"
                    f"class {feature_slug_pascal}Create({feature_slug_pascal}Base):\n"
                    f"    pass\n\n"
                    f"class {feature_slug_pascal}({feature_slug_pascal}Base):\n"
                    f"    id: int\n"
                    f"    class Config:\n"
                    f"        orm_mode = True\n"
                )
             print(f"  Appended schemas for {feature_slug_pascal} to: {schemas_file}")
        else:
            # Create if doesn't exist (though it should from Action 1)
             schemas_file.write_text(
                f"from pydantic import BaseModel\n"
                f"from typing import Optional\n\n"
                f"# Schemas for {feature_slug_pascal}\n"
                f"class {feature_slug_pascal}Base(BaseModel):\n"
                f"    # ... \n"
                f"    pass \n"
                # ... and so on
            )
             print(f"  Created: {schemas_file} (with {feature_slug_pascal} stubs)")


    def scaffold_frontend(feature_slug_snake, feature_slug_pascal):
        print(f"\nScaffolding frontend for feature: {feature_slug_pascal}")

        # Components
        comp_dir = FRONTEND_ROOT / "components" / feature_slug_pascal
        comp_file = comp_dir / f"{feature_slug_pascal}Card.tsx" # Example component
        comp_dir.mkdir(parents=True, exist_ok=True)
        if not comp_file.exists():
            comp_file.write_text(
                f"import React from 'react';\n\n"
                f"interface {feature_slug_pascal}CardProps {{\n"
                f"  // Define props here\n"
                f"  name: string;\n"
                f"}}\n\n"
                f"const {feature_slug_pascal}Card: React.FC<{feature_slug_pascal}CardProps> = ({{ name }}) => {{\n"
                f"  return (\n"
                f"    <div>\n"
                f"      <h3>{feature_slug_pascal} Card: {{name}}</h3>\n"
                f"      {/* Card content */}\n"
                f"    </div>\n"
                f"  );\n"
                f"}};\n\n"
                f"export default {feature_slug_pascal}Card;\n"
            )
            print(f"  Created: {comp_file}")

        # Pages
        page_dir = FRONTEND_ROOT / "pages"
        page_file = page_dir / f"{feature_slug_pascal}Page.tsx"
        page_dir.mkdir(parents=True, exist_ok=True)
        if not page_file.exists():
            page_file.write_text(
                f"import React from 'react';\n"
                f"// import {feature_slug_pascal}Card from '../components/{feature_slug_pascal}/{feature_slug_pascal}Card';\n\n"
                f"const {feature_slug_pascal}Page: React.FC = () => {{\n"
                f"  // Fetch data, manage state\n"
                f"  return (\n"
                f"    <div>\n"
                f"      <h1>{feature_slug_pascal} Page</h1>\n"
                f"      {/* <{feature_slug_pascal}Card name=\"Example\" /> */}\n"
                f"    </div>\n"
                f"  );\n"
                f"}};\n\n"
                f"export default {feature_slug_pascal}Page;\n"
            )
            print(f"  Created: {page_file}")
        
        # Services
        service_file = FRONTEND_ROOT / "services" / f"{feature_slug_snake}Api.ts"
        (FRONTEND_ROOT / "services").mkdir(parents=True, exist_ok=True)
        if not service_file.exists():
            service_file.write_text(
                f"// API service for {feature_slug_pascal}\n"
                f"// import {{ {feature_slug_pascal} }} from '../types/{feature_slug_snake}';\n\n"
                f"const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';\n\n"
                f"export const get{feature_slug_pascal}s = async (): Promise<any[]> => {{\n"
                f"  // const response = await fetch(`${{API_URL}}/api/v1/{feature_slug_snake}s/`);\n"
                f"  // if (!response.ok) throw new Error('Failed to fetch {feature_slug_snake}s');\n"
                f"  // return response.json();\n"
                f"  return Promise.resolve([]); // Placeholder\n"
                f"}};\n"
            )
            print(f"  Created: {service_file}")

        # Types
        type_file = FRONTEND_ROOT / "types" / f"{feature_slug_snake}.ts"
        (FRONTEND_ROOT / "types").mkdir(parents=True, exist_ok=True)
        if not type_file.exists():
            type_file.write_text(
                f"export interface {feature_slug_pascal} {{\n"
                f"  id: number;\n"
                f"  name: string;\n"
                f"  // Add other fields\n"
                f"}}\n"
            )
            print(f"  Created: {type_file}")

    def main():
        parser = argparse.ArgumentParser(description="Scaffold a new feature for the project.")
        parser.add_argument("feature_slug", help="A kebab-case or snake_case slug for the new feature (e.g., 'user-profile' or 'user_profile').")
        args = parser.parse_args()

        feature_slug_snake = to_snake_case(args.feature_slug)
        feature_slug_pascal = to_pascal_case(feature_slug_snake)

        print(f"Scaffolding feature: {args.feature_slug} (snake: {feature_slug_snake}, Pascal: {feature_slug_pascal})")

        scaffold_backend(feature_slug_snake, feature_slug_pascal)
        scaffold_frontend(feature_slug_snake, feature_slug_pascal)

        print("\nScaffolding complete. Remember to:")
        print("1. Update imports and complete the stubbed out logic.")
        print("2. Add new SQLAlchemy models to `database/models.py` and ensure `Base.metadata.create_all(bind=engine)` is called or use migrations.")
        print("3. Add new FastAPI routes in `main.py`.")
        print("4. Add frontend routes if necessary (e.g., in App.tsx).")
        print("5. Write comprehensive tests!")

    if __name__ == "__main__":
        main()
    ```
    **Add to `package.json` scripts:**
    ```diff
    --- a/package.json
    +++ b/package.json
    @@ -15,6 +15,7 @@
     "dev:clean": "pnpm reset && pnpm dev",
     "setup-env": "./repo_src/scripts/setup-env.sh",
     "setup-project": "pnpm install && python -m venv .venv && . .venv/bin/activate && pip install -r repo_src/backend/requirements.txt && pnpm setup-env",
+    "new:feature": "python repo_src/scripts/scaffold_feature.py",
     "ci": "pnpm lint && pnpm typecheck && pnpm test",
     "docs:serve": "mkdocs serve",
     "docs:build": "mkdocs build"
    ```
    **Explanation:**
    *   This Python script takes a feature slug (e.g., `user-profile`).
    *   It creates placeholder files for backend (`functions`, `adapters`, `pipelines`, `tests`, appends to `schemas.py`) and frontend (`components`, `pages`, `services`, `types`).
    *   The generated files include basic boilerplate and comments guiding the developer (or AI).
    *   Using Python for this keeps tooling consistent.
    *   The `pnpm new:feature <slug>` command makes it easy to invoke.

**3. Test and Refine `pnpm setup-project`**
The script `pnpm setup-project`: `pnpm install && python -m venv .venv && . .venv/bin/activate && pip install -r repo_src/backend/requirements.txt && pnpm setup-env`
*   This script has a common issue: `. .venv/bin/activate` only activates the venv for that specific line in the script, not for subsequent commands in the same script line or for the parent shell.
*   **Recommendation:**
    *   The Python venv activation should ideally be a separate step for the user, or the script should explicitly call the venv's pip.
    *   A more robust `setup-project` might look like:
        ```json
        "setup:venv": "python -m venv .venv",
        "setup:py-deps": ".venv/bin/pip install -r repo_src/backend/requirements.txt", // Or use platform-specific activate
        "setup-project": "pnpm install && pnpm setup:venv && pnpm setup:py-deps && pnpm setup-env"
        ```
    *   For cross-platform compatibility and to ensure the correct pip is used, it's often better to directly call `python -m pip` or `.venv/bin/pip`. The current script will work if `pip` in the PATH after venv creation points to the venv's pip, which is usually true on Linux/macOS if the venv is subsequently activated in the same shell. For a one-shot script, being explicit is safer.

    Let's adjust `setup-project` for better explicitness:
    ```diff
    --- a/package.json
    +++ b/package.json
    @@ -15,7 +15,9 @@
     "dev:clean": "pnpm reset && pnpm dev",
     "setup-env": "./repo_src/scripts/setup-env.sh",
     "setup-project": "pnpm install && python -m venv .venv && . .venv/bin/activate && pip install -r repo_src/backend/requirements.txt && pnpm setup-env",
+    "setup:py-deps": "python -m venv .venv && ./repo_src/scripts/install_py_deps.sh",
+    "setup-project": "pnpm install && pnpm setup:py-deps && pnpm setup-env",
     "new:feature": "python repo_src/scripts/scaffold_feature.py",
     "ci": "pnpm lint && pnpm typecheck && pnpm test",
     "docs:serve": "mkdocs serve",
    ```
    And create `repo_src/scripts/install_py_deps.sh`:
    ```bash
    #!/bin/bash
    # This script activates the virtual environment and installs Python dependencies.
    # It's meant to be called from pnpm scripts.

    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/.."
    VENV_PATH="${PROJECT_ROOT}/.venv"

    echo "Setting up Python virtual environment and dependencies..."

    if [ ! -d "$VENV_PATH" ]; then
        echo "Creating Python virtual environment at $VENV_PATH..."
        python -m venv "$VENV_PATH"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment."
            exit 1
        fi
    else
        echo "Virtual environment already exists at $VENV_PATH."
    fi

    # Activate venv and install requirements
    # This activation method is more robust for scripts
    if [ -f "${VENV_PATH}/bin/activate" ]; then # Linux/macOS
        # shellcheck source=/dev/null
        source "${VENV_PATH}/bin/activate"
        echo "Activated venv (Unix). Installing Python dependencies..."
        pip install -r "${PROJECT_ROOT}/repo_src/backend/requirements.txt"
        deactivate
    elif [ -f "${VENV_PATH}/Scripts/activate.bat" ]; then # Windows
        echo "Activating venv (Windows). Please run 'pip install -r repo_src/backend/requirements.txt' manually after activation if this fails."
        # Activating and running in the same cmd line is tricky for .bat
        # For now, we'll just use the venv's pip directly.
        "${VENV_PATH}/Scripts/pip.exe" install -r "${PROJECT_ROOT}/repo_src/backend/requirements.txt"
    else
        echo "Error: Could not find activate script in venv."
        exit 1
    fi

    echo "Python dependencies setup complete."
    ```
    This is a bit more involved due to cross-platform venv activation in scripts but aims for more reliability. Simpler for `setup-project` could be: `python -m venv .venv && .venv/bin/python -m pip install -r repo_src/backend/requirements.txt` for the pip install part, assuming `.venv/bin/python` exists.

    Let's use the direct python executable from the venv:
    ```diff
    --- a/package.json
    +++ b/package.json
    @@ -15,8 +15,7 @@
     "dev:clean": "pnpm reset && pnpm dev",
     "setup-env": "./repo_src/scripts/setup-env.sh",
     "setup-project": "pnpm install && python -m venv .venv && . .venv/bin/activate && pip install -r repo_src/backend/requirements.txt && pnpm setup-env",
-    "setup:py-deps": "python -m venv .venv && ./repo_src/scripts/install_py_deps.sh",
-    "setup-project": "pnpm install && pnpm setup:py-deps && pnpm setup-env",
+    "setup-project": "pnpm install && python -m venv .venv && ./.venv/bin/python -m pip install -r repo_src/backend/requirements.txt && pnpm setup-env",
     "new:feature": "python repo_src/scripts/scaffold_feature.py",
     "ci": "pnpm lint && pnpm typecheck && pnpm test",
     "docs:serve": "mkdocs serve",
    ```
    (And remove the `setup:py-deps` line and the `install_py_deps.sh` script as this direct call is cleaner for a single command). This assumes a Unix-like environment for `.venv/bin/python`. For Windows, it would be `.venv\Scripts\python.exe`. The CI uses Linux, so this is fine for CI. Local Windows users might need a slight adjustment or use WSL.

**Explanation for Action 7:**
Streamlined developer tooling enhances productivity for both humans and AI:
*   **`setup-env.sh`:** Ensures consistent and safe environment variable setup, preventing accidental overwrites. AI agents performing setup tasks can reliably use this.
*   **`scaffold_feature.py`:**
    *   Reduces boilerplate for humans.
    *   Provides a structured way for AI to initiate new features. If an AI agent is tasked to "start feature X," it can be guided to call this script, ensuring files are created in the correct locations and with initial content adhering to the project's architecture. This promotes consistency.
*   **`pnpm setup-project`:** A reliable one-command setup is crucial for quick onboarding of human developers and for CI environments or automated agents that might need to set up the project from scratch.

## Action 8: Address Inconsistencies and Consolidate

*Goal: Ensure the repository is coherent, easy to understand, and that configurations are aligned.*

**1. Path Consistency:**
This has been addressed throughout the implementation of previous actions:
*   `export_context.py` now outputs to `registry/` and sources from correct `repo_src/backend` and `repo_src/frontend/src` paths.
*   `setup-env.sh` uses correct relative paths to locate `.env.defaults` and target `.env` files.
*   `scaffold_feature.py` uses correct base paths for backend and frontend scaffolding.
*   All `README.md` files updated in previous steps will refer to the correct paths and structures.

**2. Tooling Versions / Model Choices:**
*   The `.aider.conf.yml.example` specifies `openrouter/anthropic/claude-3.5-sonnet`.
*   `code_builder/config.yaml` for `aider_model` currently has `anthropic/claude-3.7-sonnet`.

    Let's align them for consistency. Using the latest generally available and performant model is good. If Claude 3.7 Sonnet is widely available on OpenRouter and preferred, both should reflect that. If 3.5 Sonnet is more standard/reliable for now, then that. Let's assume **Claude 3.5 Sonnet** is the baseline for broader compatibility and that Aider has good support for it.

    **Modify `code_builder/config.yaml`:**
    ```diff
    --- a/code_builder/config.yaml
    +++ b/code_builder/config.yaml
    @@ -7,7 +7,7 @@
     # Model Configuration (using OpenRouter model identifiers)
     # Find identifiers at https://openrouter.ai/models
     prd_generator_model: "google/gemini-2.5-pro-preview-03-25" # Model for generating PRD and Aider config
    -aider_model: "anthropic/claude-3.7-sonnet"     # Model Aider will use (ensure Aider supports this via OpenRouter)
    +aider_model: "openrouter/anthropic/claude-3.5-sonnet"     # Model Aider will use (ensure Aider supports this via OpenRouter)
                                                    # Needs to be configured in Aider's own config too (.aider.conf.yml)
     
     # Default context files that will always be loaded for PRD generation
    ```
    **Explanation:** Changed `aider_model` in `code_builder/config.yaml` to match the `openrouter/anthropic/claude-3.5-sonnet` specified in `.aider.conf.yml.example`. The `openrouter/` prefix is important if Aider is configured to use OpenRouter as its provider. If Aider is configured to use Anthropic directly, the prefix would be omitted. The example implies OpenRouter.

**Explanation for Action 8:**
Consistency is paramount for AI-friendliness:
*   **Path Consistency:** AI tools often rely on precise file paths. Inconsistent path references in documentation, scripts, or configurations can lead to AI agents failing to find files, modifying the wrong files, or generating incorrect code.
*   **Configuration Alignment (e.g., Model Names):** If different parts of the system (e.g., PRD generator vs. Aider config) refer to different models or tools for the same conceptual step, it can cause confusion for human developers and misconfiguration for automated workflows. Aligning these makes the system more predictable and easier to manage. For AI, if it's reading multiple config files for context, consistency reduces ambiguity.

This concludes the implementation and explanation for the requested actions. The repository should now be significantly more aligned with Software 3.0 principles, offering a more robust and AI-friendly starting point.