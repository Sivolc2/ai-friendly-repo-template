Okay, I'll implement the simple frontend and backend, update the backend to use `dotenv`, and ensure the `pnpm dev:clean` script and other monorepo scripts work as expected.

Here's the plan:

1.  **Backend (FastAPI)**:
    *   Ensure `python-dotenv` is correctly used in `repo_src/backend/main.py` to load the `.env` file.
    *   Add a simple API endpoint (e.g., `/api/hello`) to `repo_src/backend/main.py`.
    *   Remove the placeholder `repo_src/backend/tests/test_sample.py`.

2.  **Frontend (React + Vite)**:
    *   Create/update `repo_src/frontend/package.json` with necessary dependencies (React, Vite) and scripts (`dev`, `build`, `lint`, `test`).
    *   Add Vite configuration (`repo_src/frontend/vite.config.ts`).
    *   Add TypeScript configuration (`repo_src/frontend/tsconfig.json` and `repo_src/frontend/tsconfig.node.json`).
    *   Create the entry HTML file (`repo_src/frontend/index.html`).
    *   Create the main React application files:
        *   `repo_src/frontend/src/main.tsx` (renders the app).
        *   `repo_src/frontend/src/App.tsx` (simple component that calls the backend API).
        *   Basic CSS files (`repo_src/frontend/src/index.css`, `repo_src/frontend/src/App.css`).
    *   Update `repo_src/frontend/README_frontend.md`.
    *   Remove placeholder files: `repo_src/frontend/src/pages/index.tsx` and `repo_src/frontend/src/utils/__tests__/sample.test.ts`.

3.  **Monorepo Setup & Scripts**:
    *   Implement `repo_src/scripts/setup-env.sh` to copy `.env.defaults` to the respective frontend and backend `.env` files.
    *   Ensure `package.json` (root) scripts (`dev`, `dev:clean`, `dev:frontend`, `dev:backend`, `setup-project`) are correctly configured and functional.
    *   Update `playwright.config.ts` to use cleaner Turbo-friendly commands for starting dev servers.

Let's proceed with the changes.

```diff
--- a/playwright.config.ts
+++ b/playwright.config.ts
@@ -22,17 +22,19 @@
   projects: [
     {
       name: 'chromium',
-      use: { ...devices['Desktop Chrome'] },
+      use: { ...devices['Desktop Chrome'], channel: 'chrome' }, // Specify channel for consistency
     },
     {
       name: 'webkit',
       use: { ...devices['Desktop Safari'] },
     },
     {
+      // Firefox can sometimes be slower or have more specific driver needs for CI
+      // name: 'firefox',
+      // use: { ...devices['Desktop Firefox'] },
+    // },
+    // { // Example for Edge
       name: 'firefox',
       use: { ...devices['Desktop Firefox'] },
     },
   ],
   webServer: [
     {
-      command: 'pnpm --filter frontend run dev',
-      port: 5173,
+      command: 'pnpm --filter @workspace/frontend dev', // Updated to use turbo workspace filter
+      url: 'http://localhost:5173', // Wait for this URL to be accessible
       reuseExistingServer: !process.env.CI,
     },
     {
-      command: 'cd repo_src/backend && uvicorn main:app --port 8000',
-      port: 8000,
+      command: 'pnpm --filter @workspace/backend dev', // Updated to use turbo workspace filter
+      url: 'http://localhost:8000/docs', // Wait for FastAPI docs to be ready
       reuseExistingServer: !process.env.CI,
     },
   ],
--- a/repo_src/backend/main.py
+++ b/repo_src/backend/main.py
@@ -35,6 +35,11 @@
     """A simple root endpoint to confirm the API is running."""
     return {"message": "Welcome to the Backend API. Database is initialized."}
 
+@app.get("/api/hello")
+async def read_hello():
+    """A simple API endpoint to be called by the frontend."""
+    return {"message": "Hello from FastAPI Backend!"}
+
 # Example (commented out) CRUD endpoints would go here
 # You would typically put these in separate router files (e.g., in an `api` or `routers` directory)
 # and include them in the main app.
--- a/repo_src/backend/tests/test_sample.py
+++ /dev/null
diff --git a/repo_src/backend/tests/test_sample.py b/repo_src/backend/tests/test_sample.py
deleted file mode 100644
index e69de29..0000000
--- a/repo_src/frontend/README_frontend.md
+++ b/repo_src/frontend/README_frontend.md
@@ -1 +1,48 @@
--e 
+## Frontend Application (React + Vite)
+
+This directory contains the frontend application built with React, TypeScript, and Vite.
+
+## Setup
+
+1.  Ensure you are in the project root directory.
+2.  Install dependencies (this is typically done via `pnpm install` in the root, which handles workspace dependencies):
+    ```bash
+    pnpm install
+    ```
+3.  Set up environment variables. Copy `.env.defaults` from the project root to `repo_src/frontend/.env` if you haven't already run `pnpm setup-env`:
+    ```bash
+    # From project root:
+    # pnpm setup-env
+    # Or manually:
+    cp ../../.env.defaults .env
+    ```
+    Adjust `VITE_API_URL` in `.env` if your backend runs on a different port or URL.
+
+## Development
+
+To run the frontend development server:
+
+```bash
+# From project root
+pnpm dev:frontend
+
+# Or from this directory (repo_src/frontend)
+pnpm dev
+```
+
+The application will be available at `http://localhost:5173` (or another port if 5173 is busy).
+
+## Build
+
+To build the application for production:
+
+```bash
+# From project root
+pnpm --filter @workspace/frontend build
+
+# Or from this directory (repo_src/frontend)
+pnpm build
+```
+The production-ready files will be in the `dist` directory.
+
+## Linting and Type Checking
+
+```bash
+# From project root
+pnpm --filter @workspace/frontend lint
+pnpm --filter @workspace/frontend typecheck
+
+# Or from this directory
+pnpm lint
+pnpm typecheck
+```
+
+## Testing
+(Vitest setup is basic - expand as needed)
+```bash
+# From project root
+pnpm --filter @workspace/frontend test
+
+# Or from this directory
+pnpm test
+```
--- a/repo_src/frontend/package.json
+++ b/repo_src/frontend/package.json
@@ -1 +1,29 @@
- -e 
+{
+  "name": "@workspace/frontend",
+  "private": true,
+  "version": "0.0.0",
+  "type": "module",
+  "scripts": {
+    "dev": "vite",
+    "build": "tsc && vite build",
+    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
+    "preview": "vite preview",
+    "test": "vitest"
+  },
+  "dependencies": {
+    "react": "^18.2.0",
+    "react-dom": "^18.2.0"
+  },
+  "devDependencies": {
+    "@types/react": "^18.2.66",
+    "@types/react-dom": "^18.2.22",
+    "@typescript-eslint/eslint-plugin": "^7.2.0",
+    "@typescript-eslint/parser": "^7.2.0",
+    "@vitejs/plugin-react": "^4.2.1",
+    "eslint": "^8.57.0",
+    "eslint-plugin-react-hooks": "^4.6.0",
+    "eslint-plugin-react-refresh": "^0.4.6",
+    "typescript": "^5.2.2",
+    "vite": "^5.2.0",
+    "vitest": "^1.3.1"
+  }
+}
--- a/repo_src/frontend/src/App.tsx
+++ b/repo_src/frontend/src/App.tsx
@@ -1 +1,37 @@
--e 
+import { useState, useEffect } from 'react'
+import './App.css' // Optional: for App specific styling
+
+function App() {
+  const [count, setCount] = useState(0)
+  const [message, setMessage] = useState('')
+  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
+
+
+  useEffect(() => {
+    fetch(`${apiUrl}/api/hello`)
+      .then(response => response.json())
+      .then(data => setMessage(data.message))
+      .catch(error => {
+         console.error("Error fetching hello API:", error);
+         setMessage("Failed to fetch message from backend.");
+      });
+  }, [apiUrl]);
+
+  return (
+    <>
+      <h1>Vite + React Frontend</h1>
+      <div className="card">
+        <button onClick={() => setCount((count) => count + 1)}>
+          count is {count}
+        </button>
+        <p>
+          Edit <code>src/App.tsx</code> and save to test HMR
+        </p>
+      </div>
+      <p className="read-the-docs">
+        Message from backend: <strong>{message}</strong>
+      </p>
+      <p>API URL is: {apiUrl}</p>
+    </>
+  )
+}
+
+export default App
--- a/repo_src/frontend/src/pages/index.tsx
+++ /dev/null
diff --git a/repo_src/frontend/src/pages/index.tsx b/repo_src/frontend/src/pages/index.tsx
deleted file mode 100644
index e69de29..0000000
--- a/repo_src/frontend/src/utils/__tests__/sample.test.ts
+++ /dev/null
diff --git a/repo_src/frontend/src/utils/__tests__/sample.test.ts b/repo_src/frontend/src/utils/__tests__/sample.test.ts
deleted file mode 100644
index e69de29..0000000
--- a/repo_src/scripts/setup-env.sh
+++ b/repo_src/scripts/setup-env.sh
@@ -1 +1,31 @@
- -e 
+#!/bin/bash
+
+echo "Setting up environment files..."
+
+# Define source and target paths
+DEFAULT_ENV_FILE=".env.defaults"
+FRONTEND_ENV_DIR="repo_src/frontend"
+BACKEND_ENV_DIR="repo_src/backend"
+FRONTEND_ENV_FILE_TARGET="${FRONTEND_ENV_DIR}/.env"
+BACKEND_ENV_FILE_TARGET="${BACKEND_ENV_DIR}/.env"
+
+# Check if .env.defaults exists
+if [ ! -f "$DEFAULT_ENV_FILE" ]; then
+    echo "Error: $DEFAULT_ENV_FILE not found in project root."
+    exit 1
+fi
+
+# Create frontend .env if it doesn't exist
+if [ ! -f "$FRONTEND_ENV_FILE_TARGET" ]; then
+    echo "Creating ${FRONTEND_ENV_FILE_TARGET} from ${DEFAULT_ENV_FILE}..."
+    cp "$DEFAULT_ENV_FILE" "$FRONTEND_ENV_FILE_TARGET"
+else
+    echo "${FRONTEND_ENV_FILE_TARGET} already exists. Skipping."
+fi
+
+# Create backend .env if it doesn't exist
+if [ ! -f "$BACKEND_ENV_FILE_TARGET" ]; then
+    echo "Creating ${BACKEND_ENV_FILE_TARGET} from ${DEFAULT_ENV_FILE}..."
+    cp "$DEFAULT_ENV_FILE" "$BACKEND_ENV_FILE_TARGET"
+else
+    echo "${BACKEND_ENV_FILE_TARGET} already exists. Skipping."
+fi
+
+echo "Environment file setup complete."
+echo "Please review the .env files in ${FRONTEND_ENV_DIR} and ${BACKEND_ENV_DIR} and customize if necessary."
\ No newline at end of file
+chmod +x repo_src/scripts/setup-env.sh
\ No newline at end of file
```
```diff
--- a/repo_src/frontend/index.html
+++ b/repo_src/frontend/index.html
@@ -0,0 +1,13 @@
+<!doctype html>
+<html lang="en">
+  <head>
+    <meta charset="UTF-8" />
+    <link rel="icon" type="image/svg+xml" href="/vite.svg" /> <!-- Default Vite icon -->
+    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
+    <title>%VITE_APP_TITLE%</title> <!-- Vite replaces this -->
+  </head>
+  <body>
+    <div id="root"></div>
+    <script type="module" src="/src/main.tsx"></script>
+  </body>
+</html>
--- /dev/null
+++ b/repo_src/frontend/src/App.css
@@ -0,0 +1,5 @@
+.card {
+  padding: 2em;
+}
+.read-the-docs {
+  color: #888;
+}
--- /dev/null
+++ b/repo_src/frontend/src/index.css
@@ -0,0 +1,18 @@
+/* Basic styles, can be expanded */
+body {
+  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
+  margin: 0;
+  padding: 20px;
+  background-color: #f0f2f5;
+  color: #1c1e21;
+  display: flex;
+  justify-content: center;
+}
+#root {
+  max-width: 800px;
+  width: 100%;
+  background-color: #fff;
+  padding: 20px;
+  border-radius: 8px;
+  box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
+}
+button {
+  padding: 10px 15px;
+  font-size: 1em;
+  cursor: pointer;
+  border-radius: 6px;
+  border: 1px solid transparent;
+  background-color: #007bff;
+  color: white;
+  margin-top: 10px;
+}
+button:hover {
+  background-color: #0056b3;
+}
+code {
+  background-color: #f8f9fa;
+  padding: 0.2em 0.4em;
+  border-radius: 3px;
+}
--- /dev/null
+++ b/repo_src/frontend/src/main.tsx
@@ -0,0 +1,11 @@
+import React from 'react'
+import ReactDOM from 'react-dom/client'
+import App from './App.tsx'
+import './index.css' // Optional: for basic styling
+
+ReactDOM.createRoot(document.getElementById('root')!).render(
+  <React.StrictMode>
+    <App />
+  </React.StrictMode>,
+)
+
--- /dev/null
+++ b/repo_src/frontend/tsconfig.json
@@ -0,0 +1,28 @@
+{
+  "compilerOptions": {
+    "target": "ES2020",
+    "useDefineForClassFields": true,
+    "lib": ["ES2020", "DOM", "DOM.Iterable"],
+    "module": "ESNext",
+    "skipLibCheck": true,
+
+    /* Bundler mode */
+    "moduleResolution": "bundler",
+    "allowImportingTsExtensions": true,
+    "resolveJsonModule": true,
+    "isolatedModules": true,
+    "noEmit": true,
+    "jsx": "react-jsx",
+
+    /* Linting */
+    "strict": true,
+    "noUnusedLocals": true,
+    "noUnusedParameters": true,
+    "noFallthroughCasesInSwitch": true,
+    "baseUrl": ".",
+    "paths": {
+      "@/*": ["src/*"]
+    }
+  },
+  "include": ["src"],
+  "references": [{ "path": "./tsconfig.node.json" }]
+}
--- /dev/null
+++ b/repo_src/frontend/tsconfig.node.json
@@ -0,0 +1,9 @@
+{
+  "compilerOptions": {
+    "composite": true,
+    "skipLibCheck": true,
+    "module": "ESNext",
+    "moduleResolution": "bundler",
+    "allowSyntheticDefaultImports": true
+  },
+  "include": ["vite.config.ts"]
+}
--- /dev/null
+++ b/repo_src/frontend/vite.config.ts
@@ -0,0 +1,11 @@
+import { defineConfig } from 'vite'
+import react from '@vitejs/plugin-react'
+
+// https://vitejs.dev/config/
+export default defineConfig({
+  plugins: [react()],
+  server: {
+    port: 5173, // Default Vite port
+    host: true, // Allow access from network
+  },
+})
```