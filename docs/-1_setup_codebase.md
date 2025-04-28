Below is a **“green-field” setup playbook** you can paste into a fresh terminal (or Cursor’s task runner) to create the *skeleton only*—no app logic, just docs, scaffolds, and rules.

---

## 1 · Prerequisites

* **pnpm** ≥ 8 (`npm i -g pnpm`)
* **Node** ≥ 20  
* **Git**  
* (optional) **Python 3.12** if you’ll write `gen_context` in Python instead of TS

---

## 2 · Repo Bootstrap

> ```bash
> pnpm init -y
> pnpm add -w -D typescript ts-node prettier
> ```

### 2.1 Workspace layout

```bash
mkdir -p docs/adr registry scripts
mkdir -p packages/backend/{core,adapters,modules/_template}  # backend
mkdir -p packages/frontend/src/{shared,app,features/_template}
```

Add **pnpm-workspaces.yaml**

```yaml
packages:
  - packages/*
  - packages/*/src  # for tsc references
```

Add blank **tsconfig.json** at root (Cursor will extend it later).

---

## 3 · Documentation Files

### 3.1 Top-level docs

| Path | Purpose | Minimal seed content |
|------|---------|----------------------|
| **docs/00_project_vision.md** | 1-paragraph “why this repo exists”. | “Framework Zero aims to…” |
| **docs/01_architecture_overview.mmd** | Mermaid system diagram. Starts with placeholder graph. | ```mermaid graph TD; A[UI]-->B[API]``` |
| **docs/02_rules_of_change.md** | *Governance rules* (R1–R5). | Copy rules table from previous answer. |
| **docs/adr/000_template.md** | ADR template. | Title, Context, Decision, Consequences sections. |

### 3.2 Package-level guides (templates)

Create **packages/backend/README_implementation_guide.md**

```md
# Backend Implementation Guide

## When to add a **module** vs. edit core  
<guidance>

## Scaffold a feature slice

```bash
pnpm new-feature backend <slice-name>
```

### Five required steps
1. Fill INTENT in README_context.md  
2. Implement service logic (≤200 LOC per class)  
3. Expose via `register(app)`  
4. Update shared schemas if needed  
5. Run `pnpm gen:context backend`
```

Duplicate and adjust for **packages/frontend/README_implementation_guide.md** (React specifics).

### 3.3 Slice README template

`packages/backend/modules/_template/README_context.md` (same for frontend slice)

```md
<!-- INTENT: <replace with 1-2 sentences> -->

<!-- FILE INDEX: auto-generated -->

<!-- PUBLIC API: auto-generated -->
```

---

## 4 · Scaffold & Utility Scripts

### 4.1 `scripts/new-feature.ts`

Skeleton (leave `TODO` markers for now):

```ts
#!/usr/bin/env ts-node
import { mkdirSync, copyFileSync } from "fs";
const [pkg, name] = process.argv.slice(2);
if (!pkg || !name) {
  console.error("Usage: pnpm new-feature <backend|frontend> <slice>");
  process.exit(1);
}
const base =
  pkg === "backend"
    ? "packages/backend/modules"
    : "packages/frontend/src/features";
mkdirSync(`${base}/${name}`, { recursive: true });
// copy template files
["README_context.md", /* other stubs */].forEach(f =>
  copyFileSync(`${base}/_template/${f}`, `${base}/${name}/${f}`)
);
console.log(`New feature slice created at ${base}/${name}`);
```

Add execution bit: `chmod +x scripts/new-feature.ts`.

In **package.json** root scripts:

```jsonc
{
  "scripts": {
    "new-feature": "ts-node scripts/new-feature.ts",
    "gen:context": "ts-node scripts/gen_context.ts"
  }
}
```

### 4.2 `scripts/gen_context.ts` (stub)

```ts
// Walk repo, fill FILE INDEX & PUBLIC API sections, write registry json.
// Leave TODOs – implement incrementally.
```

---

## 5 · Registry Placeholders

Create empty files:

```
touch registry/project_registry.json
echo "# Modules Index\n" > registry/modules_index.md
```

`gen_context` will overwrite them.

---

## 6 · CI Skeleton

`.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint-and-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: latest }
      - run: pnpm install
      - run: pnpm gen:context
      # later: run length-lint, test, build
```

---

## 7 · Workflow Cheat-Sheet

### 7.1 Adding a **normal feature**

1. **Read order**  
   1. `docs/02_rules_of_change.md`  
   2. `(backend|frontend)/README_implementation_guide.md`  
   3. Existing slice `README_context.md` if editing, else ignore.  
2. `pnpm new-feature backend priority-labels`  
3. Fill slice README INTENT, implement code.  
4. Run `pnpm gen:context backend` → updates docs + registry.  
5. Commit & open PR (no ADR required).

### 7.2 Adding a **cross-slice / architectural feature**

1. Same first two docs as above **plus** read `docs/01_architecture_overview.mmd`.  
2. Draft ADR in `docs/adr/NNN_<slug>.md`.  
3. Update overview diagram if needed.  
4. Implement across slices, respecting rules.  
5. Run full `pnpm gen:context`.  
6. PR must include ADR; reviewer confirms and merges.

---

That’s the entire skeleton.  
Once this is committed you can immediately:

```bash
# Example test run
pnpm new-feature backend hello-world
pnpm gen:context backend
git add .
git commit -m "chore: repo scaffolding"
```