Below is a **ready-to-paste starter-kit** for the “AI-driven, functional-core” repo we sketched.  
Copy the tree, drop the template files in place, run the bootstrap commands, and you’ll have a fully wired monorepo with CI/lint/test/docs rails already laid down.

---

## 0 ️⃣  Quick-start bootstrap

```bash
# ❶ create the repo & set up pnpm workspaces
mkdir ai-template && cd $_
git init
pnpm init -y                        # generates root package.json
pnpm dlx create-vite frontend -- --template react-ts
python -m venv .venv && source .venv/bin/activate
pip install -U pip pip-tools

# ❷ scaffold directory skeleton
mkdir -p repo_src/{backend,shared,scripts} docs/{adr,prd,diagrams,pipelines}
mv frontend repo_src/frontend
```

> **Tip:** keep backend as “bare” Python (no framework) until you plug in FastAPI/Starlette during the first feature.

---

## 1 ️⃣  Repository layout

```
.
├── repo_src
│   ├── backend
│   │   ├── data/         # immutable schemas/constants
│   │   ├── functions/    # pure functions
│   │   ├── pipelines/    # orchestration layers
│   │   ├── adapters/     # DB / HTTP side-effect wrappers
│   │   ├── utils/        # generic helpers
│   │   ├── tests/
│   │   ├── main.py
│   │   └── README_backend.md
│   ├── frontend
│   │   └── … (vite tree) + README_frontend.md
│   ├── shared            # generated types, OpenAPI, protobuf, etc.
│   │   └── README_shared.md
│   └── scripts
│       ├── export_context.py
│       └── README_scripts.md
├── docs
│   ├── adr/
│   ├── prd/
│   ├── diagrams/
│   ├── pipelines/        # auto-generated per-pipeline md
│   └── README_docs.md
├── .github/workflows/ci.yml
└── README.md             # project overview
```

---

## 2 ️⃣  Root `package.json`

```jsonc
{
  "name": "ai-template",
  "private": true,
  "packageManager": "pnpm@9.1.0",
  "workspaces": [
    "repo_src/*"
  ],
  "scripts": {
    "lint": "pnpm -r lint",
    "typecheck": "pnpm -r typecheck",
    "test": "pnpm -r test",
    "ctx:sync": "python repo_src/scripts/export_context.py",
    "new:feature": "node repo_src/scripts/scaffold_feature.js",
    "docs:serve": "mkdocs serve",
    "docs:build": "mkdocs build"
  },
  "devDependencies": {
    "@commitlint/cli": "^19.3.0",       // optional — you asked to skip hook
    "@typescript-eslint/parser": "^8.0.0",
    "eslint": "^8.55.0",
    "eslint-plugin-functional": "^5.0.0",
    "prettier": "^3.2.5"
  }
}
```

> **pnpm workspaces** give each package its own `package.json` (frontend already has one).  
> Back-end Python deps go in `pyproject.toml` or a `requirements.in → .txt` pair managed by **pip-tools**.

---

## 3 ️⃣  The mandatory READMEs

Below are *outline* bullets; fill in details as your team evolves.

| File | Purpose |
|------|---------|
| **README.md** | Vision, architecture diagram, quick-start, badge links to CI & docs |
| **repo_src/backend/README_backend.md** | Runtime diagram, ports/adapters explanation, local dev (`uvicorn main:app --reload`) |
| **repo_src/backend/data/README_data.md** | Style guide for frozen dataclasses / Pydantic models |
| **repo_src/backend/functions/README_functions.md** | “How to write a pure function” checklist (input types, no prints, docstring pattern) |
| **repo_src/backend/pipelines/README_pipelines.md** | Contract for orchestrators, example of composing + error surface |
| **repo_src/frontend/README_frontend.md** | Yarn scripts, Storybook, Tailwind theme switcher |
| **repo_src/shared/README_shared.md** | Describe code-gen flow: OpenAPI → TS & Pydantic models |
| **repo_src/scripts/README_scripts.md** | List every helper script & its CLI |
| **docs/README_docs.md** | mkdocs structure, how to publish to GH Pages |
| **docs/adr/README_adr.md** | Template for Architecture Decision Records |
| **docs/prd/README_prd.md** | PRD template + acceptance-criteria grammar |

Put a single-line title at the top of each README that matches the folder name; LLM-agents often treat the first line as the “page title”.

---

---

## 5 ️⃣  Context-tracker script (`repo_src/scripts/export_context.py`)

```python
#!/usr/bin/env python
"""
Walk backend & frontend dirs and emit:
  docs/pipelines/FILENAME.md     – human-readable summary
  context/context.json           – machine-readable for LLM prompts
"""
import ast, json, hashlib, textwrap, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKGS = ["repo_src/backend", "repo_src/frontend"]

funcs = []
for pkg in PKGS:
    for py in pathlib.Path(pkg).rglob("*.py"):
        if "tests" in py.parts or py.name.startswith("_"):
            continue
        node = ast.parse(py.read_text())
        for fn in [n for n in node.body if isinstance(n, ast.FunctionDef)]:
            doc = ast.get_docstring(fn) or "TODO: add docstring"
            funcs.append({
                "file": str(py.relative_to(ROOT)),
                "name": fn.name,
                "args": [a.arg for a in fn.args.args],
                "doc": doc.split("\n")[0],      # first line
                "hash": hashlib.md5(ast.unparse(fn).encode()).hexdigest()[:8]
            })

# write machine ctx
ctx_dir = ROOT / "context"
ctx_dir.mkdir(exist_ok=True)
(ctx_dir / "context.json").write_text(json.dumps(funcs, indent=2))

# write pretty md per pipeline
md = ["| Function | Args | Summary |", "|---|---|---|"]
for f in funcs:
    md.append(f"| `{f['name']}` | {', '.join(f['args'])} | {f['doc']} |")
(ROOT / "docs/pipelines/functions.md").write_text("\n".join(md))
print(f"Exported {len(funcs)} functions")
```

Add to **CI**:

```yaml
- name: Check context drift
  run: |
    pnpm ctx:sync
    git diff --exit-code docs/pipelines context/context.json
```

---

## 6 ️⃣  Scaffold-feature helper (`repo_src/scripts/scaffold_feature.js`)

Pseudo-code—create stub dirs/tests/docs in both repo_src (left as exercise to flesh out):

```js
#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
const [slug] = process.argv.slice(2);
if (!slug) throw new Error("Usage: pnpm new:feature <slug>");
const paths = [
  `repo_src/backend/functions/${slug}`,
  `repo_src/backend/tests/${slug}`,
  `repo_src/frontend/src/components/${slug}`
];
paths.forEach(p => mkdirSync(p, { recursive: true }));
writeFileSync(`repo_src/backend/functions/${slug}/README_${slug}.md`,
  `# ${slug}\n\n> Pure functions for …`);
console.log(`Feature “${slug}” scaffolded`);
```

---

## 7 ️⃣  Developer **feature flow** (README excerpt)

> Place the table below in `docs/feature_flow.md` and link to it from the root README.

| Step | Command / action | Output & gate |
|------|------------------|---------------|
| **1. Draft PRD** | Create `docs/prd/NNN-<slug>.md` | Must list *acceptance criteria* |
| **2. Scaffold** | `pnpm new:feature <slug>` | Stub dirs, failing tests |
| **3. Red tests** | Author unit tests in `backend/tests/<slug>/` | CI must show failures |
| **4. Implement** | Write pure functions until tests pass | `pnpm test` ✔ |
| **5. Compose pipeline** | Add orchestrator in `pipelines/` | Pipeline tests green |
| **6. Wire adapters** | (If needed) add side-effect impl in `adapters/` | Integration tests green |
| **7. Sync docs** | `pnpm ctx:sync` | No drift detected |
| **8. Open PR** | - | CI: lint, type, test, ctx |
| **9. Merge** | — | Done |

---

## 8 ️⃣  CI skeleton (`.github/workflows/ci.yml`)

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: pnpm/action-setup@v3
      with: { version: 9 }
    - run: pnpm install --frozen-lockfile
    - name: Type-check & lint & test
      run: |
        pnpm lint
        pnpm typecheck
        pnpm test
    - name: Context sync
      run: pnpm ctx:sync
    - name: Detect drift
      run: git diff --exit-code docs/pipelines context/context.json
```

*(You can layer Python tox/mypy steps the same way.)*

---

## 9 ️⃣  Local developer UX

```bash
# 1. install tooling
pnpm install           # FE deps
pip-sync requirements.txt

# 2. run everything
pnpm --filter frontend dev      # vite
uvicorn repo_src.backend.main:app --reload
pnpm docs:serve                 # live mkdocs
```

---

### That’s the full skeleton 🎉

* Clone → run the bootstrap → tweak package versions → start shipping.  
* When you’re ready for the first concrete feature, ping me and I’ll generate the exact scaffold files & starter tests for it.*