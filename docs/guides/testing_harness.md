Below is a pattern that has worked well on mixed **Python + TypeScript monorepos** when you want to fire *every* test suite from the root with a single `pnpm test` but still keep each language’s tooling happy and isolated.

---

## 1. Testing layers you probably want

| Layer | Package(s) | Framework | What it checks |
|-------|------------|-----------|----------------|
| **Unit** | backend | **pytest + hypothesis** | Pure‐function behaviour, property cases |
| | frontend | **Vitest + @testing-library/react** | Components, hooks, pure helpers |
| **Pipeline / integration** | backend | **pytest-asyncio** (or `pytest` with an in-memory adapter) | Orchestrators calling faked ports |
| **Contract / API** | backend ↔ frontend | **Schemathesis** (OpenAPI fuzz) | The generated client really matches server responses |
| **E2E** | root | **Playwright** | Browser flows against a dev container |
| **Static checks** | all | Ruff, mypy, ESLint-functional, ts-strict, style/format hooks | Fast feedback before tests |

You can add or drop layers, but wiring them once at the root keeps the developer UX simple.

---

## 2. Wiring Python tests so `pnpm` can see them

1. **Backend keeps its own virtual-env** (`.venv/`) and requirements:

    ```bash
    cd repo_src/backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt          # pytest, hypothesis, etc.
    ```

2. Expose a small **nox** (or **tox**) shim so Node world can run Python:

    ```python
    # repo_src/backend/noxfile.py
    import nox

    @nox.session(python="3.12")
    def tests(session):
        session.install("-r", "requirements.txt")
        session.run("pytest", "-q", "--cov=repo_src.backend")
    ```

3. Add a **package.json** in `repo_src/backend/` that points its `test` script at nox:

    ```json
    {
      "name": "@workspace/backend",
      "private": true,
      "scripts": {
        "test": "nox -s tests",
        "typecheck": "mypy ."
      }
    }
    ```

Because it’s a workspace package, the root `pnpm` can now run it like any other JS package.

---

## 3. Frontend test wiring

`repo_src/frontend/package.json` already has scripts from Vite; extend them:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint src --max-warnings 0",
    "test": "vitest run --coverage",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "vitest": "^1.4.0",
    "@testing-library/react": "^15.0.0"
  }
}
```

---

## 4. Root-level orchestration with **pnpm workspaces**

```jsonc
// root package.json
{
  "scripts": {
    // lint and type-check every package first (fast)
    "lint":       "pnpm -r run lint",
    "typecheck":  "pnpm -r run typecheck",
    // unit + integration + e2e (can be parallelised if your CI allows)
    "test":       "pnpm -r --parallel run test",
    "coverage":   "pnpm -r --parallel run coverage",
    // convenience: everything in order
    "ci":         "pnpm lint && pnpm typecheck && pnpm test"
  }
}
```

*What happens when you run `pnpm test`?*

1. `pnpm` walks every workspace (`frontend`, `backend`, any future libs)
2. Executes each package’s `test` script in its own process
3. Streams output to the root console; non-zero exit → root job fails

---

## 5. Environment-variable strategy

### Option A – **Central root `.env` plus namespacing** (favoured for small teams)

```
# .env
FRONTEND_PUBLIC_API_URL=http://localhost:8000
BACKEND_DB_URL=postgresql://postgres:postgres@localhost:5432/app
JWT_SECRET=SuperSecret
```

*How it works*

* Frontend’s Vite config loads `dotenv` and prefixes only `FRONTEND_` variables into `import.meta.env`.
* Backend (FastAPI, etc.) loads the same file with `python-dotenv` but only consumes variables starting `BACKEND_` or shared (`JWT_SECRET`).

This keeps “one file to edit” while preventing accidental leakage of server secrets to the browser.

### Option B – **Per-package `.env` files** (scales to many micro-services)

```
repo_src/backend/.env
repo_src/frontend/.env
```

You can still keep a **`.env.defaults`** in the root so new contributors run `cp .env.defaults .env` once.

> **Tip:** add `*.env*` to `.gitignore` and commit **only** example files (`.env.example`).

---

## 6. Capturing the back-end virtual-env in CI

A simple pattern:

```yaml
# .github/workflows/ci.yml
- name: Set up Python
  uses: actions/setup-python@v5
  with: { python-version: 3.12 }

- name: Cache backend venv
  uses: actions/cache@v4
  with:
    path: repo_src/backend/.venv
    key: venv-${{ runner.os }}-${{ hashFiles('repo_src/backend/requirements.txt') }}

- name: Install backend deps
  run: |
    python -m venv repo_src/backend/.venv
    . repo_src/backend/.venv/bin/activate
    pip install -r repo_src/backend/requirements.txt
```

This way the cached `.venv` is reused between workflow runs, and your JavaScript tests can still run in the same job.

---

## 7. E2E tests that span both worlds

* Put Playwright config at the root so the command is simply `pnpm e2e`.
* The script spins up:

  ```json
  "e2e": "concurrently -k "
          "\"pnpm --filter frontend run dev\" "
          "\"uvicorn repo_src.backend.main:app --reload\" "
          "\"playwright test\""
  ```

  Or use `docker compose up` in a pre-test step to bring Postgres, Redis, etc.

---

## 8. One-liner cheatsheet for contributors

```
pnpm i                # installs FE deps & all workspace package.json files
python -m venv .venv && source .venv/bin/activate
pip install -r repo_src/backend/requirements.txt
pnpm ci               # lint → typecheck → tests across the board
```

---

### Why this setup works well with LLM-assisted development

* **Single entry-point** (`pnpm test`) simplifies agent prompts: *“Run the test suite.”*
* Clear **folder-level contracts** (pure vs adapters) mean agents can reason about where to drop generated code.
* **Env namespacing** avoids secrets leaking into FE bundles without forcing devs to juggle multiple `.env` files if they don’t want to.

Feel free to tweak the exact frameworks—Vitest ↔ Jest, Playwright ↔ Cypress, nox ↔ tox—but the overall *shape* will stay useful as the project grows.