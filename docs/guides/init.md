Okay, I will create a Rust full-stack template repository using Leptos v0.6 and Axum (via `cargo-leptos`), with SQLx for database interaction (SQLite). This template will mirror the key aspects of the AI-friendly repository structure you provided, focusing on developer experience, clear project organization, and a sample application.

Here's the breakdown and implementation plan:

**1. Key Components to Implement:**

*   **Monorepo Structure:** A Rust workspace with distinct crates for the application logic (`app`) and shared data types (`shared`), housed within a `repo_src` directory.
*   **Backend & Frontend in One `app` Crate:** Leveraging `cargo-leptos`, the `app` crate will contain both the Leptos frontend UI and the Axum-based backend logic (including API handlers via server functions and database interactions). Conditional compilation (`cfg(feature = "ssr")`) will separate server-side code.
*   **Database:** SQLx with SQLite. Includes migrations and CRUD operations for a sample "items" feature.
*   **Sample Feature:** A simple list manager:
    *   Input field to add items.
    *   Display of items in a list.
    *   Ability to remove items from the list.
    *   All operations persist to the SQLite database.
*   **Unified Development Command:** `cargo leptos watch` will provide hot-reloading for both frontend and backend.
*   **Separate Build/Run:** Standard `cargo build`, `cargo run`, and `cargo leptos build --release` will be available.
*   **Documentation & Guides:**
    *   Root `README.md`: Project overview, setup, running, building.
    *   `README.testing.md`: How to approach testing.
    *   `docs/feature_flow.md`: Guide for contributing new features.
    *   READMEs in sub-directories where appropriate (e.g., within `app/src/database.rs` as comments).
*   **Testing Examples:** Examples of testing server functions.
*   **`.gitignore`:** Tailored for Rust, `cargo-leptos`, and common OS/IDE files.
*   **Environment Configuration:** Using `.env` files for database URLs, etc.

**2. Rust Full-Stack Implementation (Leptos v0.6):**

I will generate the file contents for the following structure.

```
<project_root>/
├── .env.example
├── .gitignore
├── Cargo.toml               # Workspace root
├── README.md
├── README.testing.md
├── rust-toolchain.toml
├── docs/
│   └── feature_flow.md
└── repo_src/
    ├── app/                 # Main Leptos application (FE & BE logic)
    │   ├── Cargo.toml
    │   ├── index.html         # Main HTML file for Leptos
    │   ├── migrations/        # SQLx migrations
    │   │   └── 0001_create_items_table.sql
    │   ├── src/
    │   │   ├── app_component.rs # Main application UI component
    │   │   ├── components/      # UI components
    │   │   │   ├── item_form.rs
    │   │   │   ├── item_list.rs
    │   │   │   └── mod.rs
    │   │   ├── database.rs    # Database connection, CRUD operations
    │   │   ├── error_template.rs # Leptos error handling
    │   │   ├── lib.rs           # Crate library entry (registers components)
    │   │   ├── main.rs          # Main entry for client (WASM) and server
    │   │   └── server_fns.rs  # Leptos Server Functions
    │   └── style/
    │       └── main.css       # Basic styling
    └── shared/              # Shared data types (DTOs)
        ├── Cargo.toml
        └── src/
            └── lib.rs
```

**3. Example Frontend and Backend Logic:**

*   **Shared DTO (`shared/src/lib.rs`):**
    *   `Item` struct (id, text, created_at).
*   **Backend Logic (`app/src/database.rs`, `app/src/server_fns.rs`):**
    *   SQLx pool setup for SQLite.
    *   `CREATE TABLE items ...` migration.
    *   Server functions:
        *   `get_items() -> Result<Vec<Item>, ServerFnError>`
        *   `add_item(text: String) -> Result<(), ServerFnError>`
        *   `delete_item(id: i64) -> Result<(), ServerFnError>`
*   **Frontend UI (`app/src/app_component.rs`, `app/src/components/`):**
    *   `ItemForm` component with an input field and submit button.
    *   `ItemList` component to display items, each with a delete button.
    *   Main `AppComponent` to orchestrate fetching, adding, and deleting items using Leptos resources and actions tied to the server functions.

Let's generate the files.

--- START OF FILE repo_contents.txt ---

===== .env.example =====
# Example environment variables
# Copy this file to .env and fill in your values.

# Database URL for SQLx
# For SQLite, this can be a file path.
# Example: DATABASE_URL="sqlite:mydatabase.db?mode=rwc" (rwc = read/write/create)
# Ensure the directory exists if it's a relative path, or use an absolute path.
DATABASE_URL="sqlite:./target/dev.db?mode=rwc"

# Leptos specific environment variables (optional, defaults are usually fine)
# LEPTOS_OUTPUT_NAME="my_leptos_app"
# LEPTOS_SITE_ROOT="target/site"
# LEPTOS_SITE_PKG_DIR="pkg"
# LEPTOS_SITE_ADDR="127.0.0.1:3000"
# LEPTOS_RELOAD_PORT="3001"

===== .gitignore =====
# Rust target directory
/target/

# Cargo lock file (sometimes committed, sometimes not, depends on policy)
# For library crates, it's often ignored. For binaries/applications, it's often committed.
# As this is an application template, let's suggest committing it by not ignoring.
# Cargo.lock

# Operating System files
.DS_Store
Thumbs.db
Desktop.ini

# IDE files
.idea/
.vscode/
*.iml
*.code-workspace

# Build artifacts
*.o
*.rlib
*.so
*.dylib
*.a
*.dll
*.exe
*.pdb

# Wasm specific
repo_src/app/pkg/

# Environment files
.env
.env.*
!/.env.example

# Logs
*.log
logs/

# SQLx offline data (if used)
sqlx-data.json

# Test coverage
coverage/
tarpaulin-report.html

# editor auto-backup files
*~
*.swp
*.swo

# Node modules (if any JS tooling is used alongside, e.g. for CSS)
node_modules/

# cargo-leptos generated files in app dir that should be ignored
repo_src/app/target/ # Handled by /target/ at root, but can be explicit

# Content of this file
repo_contents.txt
---

===== Cargo.toml =====
[workspace]
resolver = "2"
members = [
    "repo_src/app",
    "repo_src/shared",
]

# Default profile for development (can be overridden in user's ~/.cargo/config.toml)
[profile.dev]
opt-level = 1 # A bit of optimization for dev builds
debug = true

# Profile for release builds
[profile.release]
opt-level = 'z' # Optimize for size. 's' is also a good option.
lto = true
codegen-units = 1
panic = "abort"
strip = "symbols" # "debuginfo" or true also works

===== README.md =====
# Rust Full-Stack Web Application Template (Leptos + Axum + SQLx)

This repository provides a template for building full-stack web applications in Rust using the Leptos framework, with Axum for the server-side backend (managed via `cargo-leptos`) and SQLx for asynchronous, compile-time checked SQL database interaction (using SQLite by default).

It's designed to be AI-friendly, encouraging clear structure, good documentation, and a straightforward development workflow.

## Features

*   **Full-Stack Rust:** Write both your frontend and backend logic in Rust.
*   **Leptos Framework (v0.6):** A modern, ergonomic Rust framework for building reactive web UIs.
*   **Axum Backend:** Integrated via `cargo-leptos` for serving the application and handling API requests (through Leptos server functions).
*   **SQLx & SQLite:** Asynchronous SQL toolkit with compile-time query checking. SQLite is used for easy setup.
*   **Hot Reloading:** `cargo leptos watch` provides a fast development loop.
*   **Monorepo Structure:** Clear separation of concerns with `app` and `shared` crates.
*   **Basic CRUD Example:** A simple item list manager demonstrates database interaction and frontend reactivity.
*   **Environment Configuration:** Uses `.env` files for managing settings like database URLs.
*   **Clear Documentation:** Guidelines for setup, development, and testing.

## Project Structure

```
.
├── .env.example         # Example environment variables
├── .gitignore
├── Cargo.toml           # Workspace root
├── README.md            # This file
├── README.testing.md    # Testing guidelines
├── rust-toolchain.toml  # Specifies Rust toolchain version
├── docs/
│   └── feature_flow.md  # Guide for adding new features
└── repo_src/
    ├── app/             # Main Leptos application (FE & BE logic)
    │   ├── Cargo.toml
    │   ├── index.html     # Main HTML file for Leptos
    │   ├── migrations/    # SQLx migrations (e.g., 0001_create_items_table.sql)
    │   ├── src/           # Source code for the app
    │   │   ├── app_component.rs
    │   │   ├── components/
    │   │   ├── database.rs
    │   │   ├── error_template.rs
    │   │   ├── lib.rs
    │   │   ├── main.rs
    │   │   └── server_fns.rs
    │   └── style/
    │       └── main.css
    └── shared/          # Shared data types (DTOs)
        ├── Cargo.toml
        └── src/
            └── lib.rs
```

## Prerequisites

*   **Rust:** Install from [rust-lang.org](https://www.rust-lang.org/tools/install). This template uses the version specified in `rust-toolchain.toml`.
*   **cargo-leptos:** Install with `cargo install cargo-leptos`.
*   **SQLx CLI (Optional but Recommended):** For managing database migrations. Install with `cargo install sqlx-cli --no-default-features --features native-tls,sqlite`.
*   **wasm32-unknown-unknown target:** `rustup target add wasm32-unknown-unknown`.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Set up environment variables:**
    Copy `.env.example` to `.env` and customize if needed (e.g., `DATABASE_URL`).
    ```bash
    cp .env.example .env
    ```
    The default `DATABASE_URL` is `sqlite:./target/dev.db?mode=rwc`. `cargo-leptos` creates the `target` directory.

3.  **Run database migrations:**
    If you have `sqlx-cli` installed and configured your `.env` file:
    ```bash
    sqlx database create # May not be needed for SQLite if file is auto-created
    sqlx migrate run --source repo_src/app/migrations
    ```
    Alternatively, the application will attempt to run migrations on startup if the `DATABASE_AUTO_MIGRATE` feature is enabled (it is by default in this template's `app/Cargo.toml`).

4.  **Run the development server:**
    ```bash
    cargo leptos watch
    ```
    This command will build the application, start a development server, and watch for file changes to enable hot reloading.
    Open your browser to `http://127.0.0.1:3000` (or the address shown in the terminal).

## Development Workflow

*   **Modify Code:** Make changes to files in `repo_src/app/src/` for application logic/UI, or `repo_src/shared/src/` for shared types.
*   **Server Functions:** Define backend logic accessible from the frontend in `repo_src/app/src/server_fns.rs`.
*   **Database Interactions:** Manage database logic in `repo_src/app/src/database.rs`.
*   **Styling:** Add CSS to `repo_src/app/style/main.css`. Ensure it's linked in `repo_src/app/index.html`.
*   **Adding Dependencies:**
    *   For the main app: `cargo add <crate_name> -p app`
    *   For shared types: `cargo add <crate_name> -p shared`

Refer to `docs/feature_flow.md` for a step-by-step guide on adding new features.

## Building for Production

```bash
cargo leptos build --release
```
This will create an optimized build in the `target/release` directory for the server binary and `target/site` for the frontend assets (WASM, JS glue, CSS).

## Running in Production

After building, you can run the server binary:
```bash
./target/release/app_name # Replace app_name with your actual binary name (see app/Cargo.toml)
```
Ensure your production environment has the necessary environment variables set (e.g., `DATABASE_URL`).

## Testing

See `README.testing.md` for guidelines on testing different parts of the application.
To run tests:
```bash
cargo test --workspace
```

## License

This template is licensed under the MIT License. See `LICENSE` file (if you add one, this template doesn't include one by default).
---

===== README.testing.md =====
# Testing Guidelines

Testing a full-stack Leptos application involves several layers. Here's a guide to approaching testing in this template:

## 1. Unit Tests for Business Logic

*   **Location:** Alongside your modules (e.g., in `repo_src/app/src/database.rs` or other logic modules).
*   **Focus:** Test pure functions, data transformations, and specific logic units in isolation.
*   **Tools:** Standard `#[test]` attribute and Rust's assertion macros.

```rust
// Example in a hypothetical utils.rs
pub fn format_username(name: &str) -> String {
    name.to_lowercase()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_username() {
        assert_eq!(format_username("TeStUser"), "testuser");
    }
}
```

## 2. Testing Server Functions

Leptos server functions can be tested as regular Rust functions, especially if they encapsulate logic that doesn't heavily depend on the `ServerFnError` context directly or can be mocked.

*   **Location:** Typically in a test module within `server_fns.rs` or a dedicated test file.
*   **Strategy:**
    *   Ensure your database connection or other dependencies can be managed during tests (e.g., using a test database, mocks).
    *   Call the server function directly.
    *   Assert the `Result` returned.

```rust
// In repo_src/app/src/server_fns.rs
// ... (your server function definitions AddItem, GetItems, DeleteItem) ...

#[cfg(test)]
mod tests {
    use super::*;
    use leptos::create_runtime; // Required for server fns to run

    // Helper to setup a test database if needed (example)
    async fn setup_test_db() -> Result<sqlx::SqlitePool, sqlx::Error> {
        let pool = crate::database::get_db_pool_test().await?;
        // Ensure migrations run for the test DB
        sqlx::migrate!("./migrations")
            .run(&pool)
            .await
            .expect("Failed to run migrations on test DB");
        Ok(pool)
    }
    
    // Cleanup helper (example)
    async fn cleanup_test_db(pool: sqlx::SqlitePool) {
        // Example: delete all items or drop tables if necessary
        sqlx::query("DELETE FROM items").execute(&pool).await.ok();
        pool.close().await;
    }


    #[tokio::test]
    async fn test_add_and_get_items() {
        let _rt = create_runtime(); // Leptos runtime for server functions
        let pool = setup_test_db().await.expect("Failed to setup test DB");
        
        // Provide the pool to your server functions,
        // This might require modifying server functions to accept a pool for testability
        // or using a static/thread_local pool configured for tests.
        // For simplicity, this example assumes server functions can access a test-configured pool.
        // In a real app, you might use `leptos::use_context` with a test pool.
        // Or, refactor database logic out of server_fns into `database.rs` and test that directly.

        // For this template, server_fns directly call database::*, which uses a global pool.
        // We'd need to ensure that global pool is configured for tests.
        // `leptos::leptos_server::use_context` is the idiomatic way to pass state like DB pools
        // to server functions during requests, which can be mocked/provided in tests.

        // Test AddItem
        let result_add = AddItem::run_internal(AddItemParams { text: "Test item from test".to_string() }).await;
        assert!(result_add.is_ok(), "Failed to add item: {:?}", result_add.err());

        // Test GetItems
        let items_result = GetItems::run_internal(GetItemsParams {}).await;
        assert!(items_result.is_ok(), "Failed to get items: {:?}", items_result.err());
        let items = items_result.unwrap();
        assert!(!items.is_empty(), "Items list should not be empty after adding.");
        assert!(items.iter().any(|item| item.text == "Test item from test"), "Test item not found in list.");
        
        cleanup_test_db(pool).await;
        _rt.dispose();
    }
    
    #[tokio::test]
    async fn test_delete_item() {
        let _rt = create_runtime();
        let pool = setup_test_db().await.expect("Failed to setup test DB");

        // Add an item first
        let add_action = AddItem::run_internal(AddItemParams { text: "Item to delete".to_string() }).await;
        assert!(add_action.is_ok());

        let items_before_delete = GetItems::run_internal(GetItemsParams {}).await.unwrap();
        let item_to_delete = items_before_delete.iter().find(|item| item.text == "Item to delete");
        assert!(item_to_delete.is_some(), "Item to delete was not added");

        // Test DeleteItem
        let delete_action = DeleteItem::run_internal(DeleteItemParams { id: item_to_delete.unwrap().id }).await;
        assert!(delete_action.is_ok(), "Failed to delete item: {:?}", delete_action.err());

        let items_after_delete = GetItems::run_internal(GetItemsParams {}).await.unwrap();
        assert!(
            !items_after_delete.iter().any(|item| item.text == "Item to delete"),
            "Item was not deleted."
        );
        
        cleanup_test_db(pool).await;
        _rt.dispose();
    }
}
```
**Note on testing server functions that access a database:**
The `database::get_db_pool()` function in this template initializes a global static pool. For testing, you'd typically want a separate test database.
The `get_db_pool_test()` function is added to `database.rs` for this purpose. Tests should ensure this test pool is used.
A more robust way for larger apps is to pass the DB pool via context (`leptos::use_context()`) in your server functions, allowing you to provide a test pool during tests. For this template, the global static approach is simpler to demonstrate but has limitations for concurrent tests if not handled carefully. The tests above assume `get_db_pool()` can be influenced or a test-specific version is used. The example `get_db_pool_test` and its usage in tests illustrate one way.

## 3. Component Logic Tests (If Applicable)

*   **Location:** In a `tests` module within your component file or a separate test file.
*   **Focus:** If your components have complex non-UI logic (e.g., data manipulation passed via props), test that logic.
*   **Leptos UI Testing:** Direct UI interaction testing (like "click a button and check text") in pure Rust is still an evolving area. Tools like `wasm-bindgen-test` can run tests in a headless browser, but setup can be complex.
*   For this template, focus on testing the logic passed *to* components or logic within server functions that components trigger.

## 4. End-to-End (E2E) Tests

*   **Focus:** Test user flows through the entire application from the browser's perspective.
*   **Tools:**
    *   **Playwright** or **Selenium:** Control a real browser to interact with your application. You'd write tests in TypeScript/JavaScript or Python.
    *   **Setup:** Requires running your Leptos application (e.g., via `cargo leptos watch` or a release build).
*   **Example (Conceptual Playwright in TS):**
    ```typescript
    // e2e/example.spec.ts
    import { test, expect } from '@playwright/test';

    test('should add and display an item', async ({ page }) => {
      await page.goto('http://127.0.0.1:3000'); // Your app URL
      await page.fill('input[type="text"]', 'My new E2E item');
      await page.click('button[type="submit"]');
      await expect(page.locator('ul > li')).toHaveText(/My new E2E item/);
    });
    ```
*   E2E tests are outside the scope of `cargo test` and require a separate test runner and setup.

## Running Tests

```bash
cargo test --workspace
```
This command will run all `#[test]` functions in your workspace. Add `-- --nocapture` to see `println!` outputs.

For tests involving `tokio` (like async server function tests):
```bash
cargo test --workspace --features blocking # If some tests need the blocking feature of tokio
```

## Tips for Testable Code

*   **Separate Concerns:** Keep UI logic (in components) separate from business logic (in server functions, helper modules, or `database.rs`).
*   **Pure Functions:** Write pure functions where possible, as they are easiest to test.
*   **Dependency Injection:** For complex scenarios, consider how dependencies (like database connections) are provided to functions, allowing for mocks or test instances to be injected. (Leptos context system can be useful here).
---

===== rust-toolchain.toml =====
[toolchain]
channel = "nightly" # Leptos often benefits from nightly features, but stable can also work.
# Or specify a specific version:
# channel = "1.7X.0"
# components = [ "rustfmt", "clippy" ]
# target = [ "wasm32-unknown-unknown" ] # Ensure this target is available
---

===== docs/feature_flow.md =====
# Feature Development Workflow (Rust Full-Stack with Leptos)

This document outlines the step-by-step process for developing new features in this repository.

| Step | Command / Action | Output & Gate | Rust/Leptos Specific Notes |
|------|------------------|---------------|----------------------------|
| **1. Understand & Plan** | Review existing code in `repo_src/app` and `repo_src/shared`. Discuss requirements. | Clear understanding of feature scope and impact. | Identify reusable components, server functions, or shared types. |
| **2. Define Data Structures** | Modify or add structs in `repo_src/shared/src/lib.rs` for DTOs. Add or modify model structs in `repo_src/app/src/models.rs` (if DB schema changes). | Clear data contracts (structs with `Serialize`, `Deserialize`, `Clone`). | Use `serde` for serialization. Ensure types are `Clone` if used in Leptos signals. |
| **3. Database Migrations (If Schema Changes)** | `sqlx migrate add <migration_name> --source repo_src/app/migrations`. Edit the new SQL file. Then run `sqlx migrate run --source repo_src/app/migrations`. | Database schema updated. SQL migration file checked in. | Ensure `DATABASE_URL` is set in `.env`. |
| **4. Implement Backend Logic (Server Functions & Database Ops)** | Add/modify functions in `repo_src/app/src/database.rs` for CRUD. Create/update server functions in `repo_src/app/src/server_fns.rs`. | Backend logic implemented and unit-testable. | Server functions should return `Result<T, ServerFnError>`. Use `sqlx` macros for queries. |
| **5. Write Backend Tests** | Add `#[test]` functions for new database logic or server functions. Use `cargo test --workspace`. | Tests pass for backend logic (Red -> Green). | Mock database interactions or use a test database. See `README.testing.md`. |
| **6. Implement Frontend Components** | Create/modify Leptos components in `repo_src/app/src/components/` and update `repo_src/app/src/app_component.rs`. | UI components created. | Use Leptos signals, derived signals, resources, and actions for reactivity. |
| **7. Connect Frontend to Backend** | In components, use `create_server_action` for mutations (add, delete) and `create_resource` for fetching data, calling the server functions. | UI interacts correctly with the backend. Data flows as expected. | Ensure params for server functions are correctly passed. Handle `Result` from server functions in UI. |
| **8. Styling** | Add/modify CSS in `repo_src/app/style/main.css`. Link classes to your components. | Feature is visually styled. | Basic CSS. For more complex styling, consider CSS frameworks or tools. |
| **9. Manual E2E & QA** | Run `cargo leptos watch`. Manually test the feature flow in the browser. | Feature works as per acceptance criteria. | Test different user inputs, edge cases, and error states. |
| **10. Refactor & Add Comments** | Clean up code, add comments where necessary. Ensure code follows Rust best practices and clippy recommendations (`cargo clippy`). | Code is clean, well-documented. | - |
| **11. Open PR** | Create Pull Request. Describe changes, link to issue/PRD. | - | CI should run `cargo clippy`, `cargo fmt --check`, `cargo test`. |
| **12. Code Review** | Human team members review the PR. | Code quality, adherence to patterns, correctness. | - |
| **13. Merge** | Merge PR after approval and passing CI. | - | - |

**Development Server:**
Keep `cargo leptos watch` running during development for hot reloading.

**Key Files for a New Feature (Example: "Comments" on Items):**

*   `repo_src/shared/src/lib.rs`: Add `Comment` struct.
*   `repo_src/app/migrations/`: New migration for `comments` table.
*   `repo_src/app/src/database.rs`: `create_comment_db`, `get_comments_for_item_db`.
*   `repo_src/app/src/server_fns.rs`: `AddComment` server function, `GetComments` server function.
*   `repo_src/app/src/components/`: `CommentForm.rs`, `CommentList.rs`.
*   `repo_src/app/src/app_component.rs` (or relevant item detail component): Integrate comment components.
---

===== repo_src/app/Cargo.toml =====
[package]
name = "app"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "rlib"]

[dependencies]
leptos = { version = "0.6", features = ["csr", "nightly", "serde"] } # Ensure nightly for latest features if needed by toolchain
leptos_meta = { version = "0.6", features = ["csr", "nightly"] }
leptos_axum = { version = "0.6", optional = true }
leptos_router = { version = "0.6", features = ["csr", "nightly"] }

# Shared types
shared = { path = "../shared" }

# Server-side (SSR) specific dependencies
axum = { version = "0.7", optional = true }
tokio = { version = "1", features = ["rt-multi-thread"], optional = true }
tower = { version = "0.4", optional = true }
tower-http = { version = "0.5", features = ["fs"], optional = true }
sqlx = { version = "0.7", features = ["runtime-tokio", "sqlite", "macros", "chrono", "uuid"], optional = true }
dotenvy = { version = "0.15", optional = true }
thiserror = { version = "1.0", optional = true }
http = { version = "1.0", optional = true } # Ensure http version compatibility
chrono = { version = "0.4", features = ["serde"], optional = true } # For timestamps

# Client-side (CSR/WASM) specific dependencies
console_error_panic_hook = { version = "0.1.7", optional = true }
console_log = { version = "1.0", optional = true }
wasm-bindgen = { version = "0.2.92", optional = true }
web-sys = { version = "0.3", features = ["HtmlInputElement", "KeyboardEvent", "Event"], optional = true }

[features]
hydrate = [
    "leptos/hydrate",
    "leptos_meta/hydrate",
    "leptos_router/hydrate",
]
ssr = [
    "dep:axum",
    "dep:tokio",
    "dep:tower",
    "dep:tower-http",
    "dep:leptos_axum",
    "dep:sqlx",
    "dep:dotenvy",
    "dep:thiserror",
    "dep:http",
    "dep:chrono",
    "leptos/ssr",
    "leptos_meta/ssr",
    "leptos_router/ssr",
]
# Default feature for development, enables auto-migration
default = ["ssr", "hydrate", "DATABASE_AUTO_MIGRATE"]

# Feature to enable automatic database migrations on server startup
DATABASE_AUTO_MIGRATE = ["sqlx"]


[package.metadata.leptos]
# The name used by wasm-bindgen/cargo-leptos for the JS/WASM bundle. Defaults to the crate name.
output-name = "app"
# The site root folder is where cargo-leptos generate all output. WARNING: all content of this folder will be erased on a rebuild. Use it in your server setup.
site-root = "target/site"
# The site-pkg-dir is where cargo-leptos generate the WASM/JS package used by the JS bundle.
site-pkg-dir = "pkg"
# The style-file is the relative path for the CSS file to use when using --style option found in Leptos.toml
style-file = "style/main.css"
# Assets dir. All files found here will be copied and served as static assets.
assets-dir = "public"
# The IP and port (ex: 127.0.0.1:3000) where the server serves the content. Use it in your server setup.
site-addr = "127.0.0.1:3000"
# The port to use for automatic reload monitoring
reload-port = 3001
# The browserlist query used for optimizing the JS bundle
browserquery = "defaults"
# Set by cargo-leptos watch when building with that tool. Controls whether autoreload JS will be included in the HTML snippet
# watch = false
# The environment Leptos will run in, usually either "DEV" or "PROD"
env = "DEV"
# The features to use when compiling the bin target
#
# Optional. Can be over-ridden with the command line parameter --bin-features
bin-features = ["ssr"]

# If the --separate-front-target-dir command line parameter is
# provided, this is the directory in which the frontend bundle is
# built. Otherwise, it defaults to "<SITE_ROOT>/front"
# front-target-dir = "target/front"

# The features to use when compiling the lib target
#
# Optional. Can be over-ridden with the command line parameter --lib-features
lib-features = ["hydrate"]

# Path to .env file that will be created if it does not exist.
# Path is relative to the directory of this Leptos.toml file.
# Creates an empty .env file if it does not exist.
env-file = "../../.env"
# Path to the Cargo.toml file for the Wassm / client side. It can be the same as the bin-cargo-manifest-path.
lib-cargo-manifest-path = "Cargo.toml"
# Path to the Cargo.toml file for the Server / bin side. It can be the same as the lib-cargo-manifest-path.
bin-cargo-manifest-path = "Cargo.toml"
# Additional arguments to forward to the wasm-bindgen CLI call.
# bin-exe-name = "app" # Keep this commented if your bin name is the same as package name

[dev-dependencies]
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
wasm-bindgen-test = "0.3.42"
---

===== repo_src/app/index.html =====
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Rust Full-Stack App</title>
    <link rel="stylesheet" href="/style/main.css">
    <link rel="icon" href="data:;base64,iVBORw0KGgo="> <!-- Simple empty favicon -->
    <!-- {{ meta }} -->
  </head>
  <body>
    <!-- {{ body }} -->
  </body>
</html>
---

===== repo_src/app/migrations/0001_create_items_table.sql =====
-- Create items table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
---

===== repo_src/app/src/app_component.rs =====
use leptos::*;
use leptos_meta::*;

use crate::components::item_form::ItemForm;
use crate::components::item_list::ItemList;
use crate::server_fns::{AddItem, AddItemParams, DeleteItem, DeleteItemParams, GetItems, GetItemsParams};
use shared::Item; // Assuming Item is in shared crate

#[component]
pub fn AppComponent() -> impl IntoView {
    provide_meta_context();

    // Action for adding an item
    let add_item_action = create_server_action::<AddItem>();

    // Action for deleting an item
    let delete_item_action = create_server_action::<DeleteItem>();

    // Resource for loading items
    // It will refetch whenever add_item_action or delete_item_action dispatches a new value
    // (i.e., after an item is successfully added or deleted)
    let items_resource = create_resource(
        move || (add_item_action.version().get(), delete_item_action.version().get()),
        |_| async move {
            match GetItems::run_internal(GetItemsParams {}).await {
                Ok(items) => items,
                Err(e) => {
                    logging::error!("Failed to fetch items: {:?}", e);
                    Vec::new() // Return empty vec on error
                }
            }
        },
    );

    let on_item_added = Callback::new(move |text: String| {
        add_item_action.dispatch(AddItemParams { text });
    });

    let on_item_deleted = Callback::new(move |id: i64| {
        delete_item_action.dispatch(DeleteItemParams { id });
    });
    
    view! {
        <Title text="Simple Item List"/>
        <main class="container">
            <h1>"Item Management"</h1>

            <div class="card">
                <h2>"Add New Item"</h2>
                <ItemForm on_submit=on_item_added submitting=add_item_action.pending() />
            </div>

            <div class="card">
                <h2>"Current Items"</h2>
                <Suspense fallback=view! { <p>"Loading items..."</p> }>
                    {move || match items_resource.get() {
                        Some(items) => {
                            if items.is_empty() {
                                view! { <p>"No items yet. Add one above!"</p> }.into_view()
                            } else {
                                view! { <ItemList items=items on_delete=on_item_deleted /> }.into_view()
                            }
                        }
                        None => view! { <p>"Loading..."</p> }.into_view(),
                    }}
                </Suspense>
                {move || {
                    let adding = add_item_action.pending().get();
                    let deleting = delete_item_action.pending().get();
                    if adding || deleting {
                        view!{ <p class="loading-indicator">Processing...</p>}
                    } else {
                        view!{ <></> }
                    }
                }}
            </div>
        </main>
    }
}
---

===== repo_src/app/src/components/item_form.rs =====
use leptos::*;

#[component]
pub fn ItemForm(
    on_submit: Callback<String>,
    submitting: ReadSignal<bool>,
) -> impl IntoView {
    let (text, set_text) = create_signal(String::new());

    let submit_handler = move |ev: ev::SubmitEvent| {
        ev.prevent_default(); // Prevent default form submission
        let current_text = text.get();
        if !current_text.trim().is_empty() {
            on_submit.call(current_text);
            set_text.set(String::new()); // Clear input after submission
        }
    };

    view! {
        <form on:submit=submit_handler class="item-form">
            <div>
                <label for="item-text">"Item Text:"</label>
                <input
                    type="text"
                    id="item-text"
                    value=move || text.get()
                    on:input=move |ev| set_text.set(event_target_value(&ev))
                    prop:disabled=move || submitting.get()
                    required
                />
            </div>
            <button type="submit" prop:disabled=move || submitting.get() class="button-primary">
                {move || if submitting.get() { "Adding..." } else { "Add Item" }}
            </button>
        </form>
    }
}
---

===== repo_src/app/src/components/item_list.rs =====
use leptos::*;
use shared::Item; // Assuming Item is in shared crate

#[component]
pub fn ItemList(
    items: Vec<Item>,
    on_delete: Callback<i64>,
) -> impl IntoView {
    if items.is_empty() {
        return view! { <p>"No items to display."</p> }.into_view();
    }

    view! {
        <ul class="item-list">
            {items.into_iter().map(|item| {
                let item_id = item.id;
                view! {
                    <li class="item">
                        <span class="item-text">{&item.text}</span>
                        <span class="item-date">
                            // Format date if you have chrono or similar
                            // {format_date(&item.created_at)}
                            {&item.created_at.to_string()} // Simple to_string for now
                        </span>
                        <button
                            on:click=move |_| on_delete.call(item_id)
                            class="item-delete"
                        >
                            "Delete"
                        </button>
                    </li>
                }
            }).collect_view()}
        </ul>
    }
}

// Helper to format date (example, if you use chrono)
// fn format_date(timestamp_str: &str) -> String {
//     use chrono::NaiveDateTime;
//     if let Ok(ndt) = NaiveDateTime::parse_from_str(timestamp_str, "%Y-%m-%d %H:%M:%S") {
//         ndt.format("%Y-%m-%d %H:%M").to_string()
//     } else {
//         timestamp_str.to_string()
//     }
// }
---

===== repo_src/app/src/components/mod.rs =====
pub mod item_form;
pub mod item_list;
---

===== repo_src/app/src/database.rs =====
use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};
use std::env;
use std::sync::OnceLock;
use leptos::ServerFnError;
use shared::Item; // Assuming Item is in shared crate
use chrono::Utc;

// Global static pool, initialized once.
static POOL: OnceLock<SqlitePool> = OnceLock::new();

async fn init_pool() -> Result<SqlitePool, sqlx::Error> {
    let database_url = env::var("DATABASE_URL")
        .map_err(|_| sqlx::Error::Configuration("DATABASE_URL not set".into()))?;
    
    SqlitePoolOptions::new()
        .max_connections(5) // Adjust as needed
        .connect(&database_url)
        .await
}

pub async fn get_db_pool() -> Result<&'static SqlitePool, sqlx::Error> {
    if POOL.get().is_none() {
        let pool = init_pool().await?;
        POOL.set(pool).map_err(|_| sqlx::Error::PoolClosed)?; // Should not happen
    }
    Ok(POOL.get().unwrap())
}

// Separate function for test database pool if needed
pub async fn get_db_pool_test() -> Result<SqlitePool, sqlx::Error> {
    let test_db_url = env::var("TEST_DATABASE_URL").unwrap_or_else(|_| "sqlite::memory:".to_string());
    SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&test_db_url)
        .await
}


// Called from main.rs on server startup if DATABASE_AUTO_MIGRATE feature is enabled
#[cfg(feature = "DATABASE_AUTO_MIGRATE")]
pub async fn run_migrations() -> Result<(), sqlx::Error> {
    leptos::logging::log!("Running database migrations...");
    let pool = get_db_pool().await?;
    sqlx::migrate!("./migrations") // Path relative to CARGO_MANIFEST_DIR of app crate
        .run(pool)
        .await?;
    leptos::logging::log!("Database migrations completed.");
    Ok(())
}


// --- CRUD Operations ---

pub async fn get_all_items_db() -> Result<Vec<Item>, ServerFnError> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    sqlx::query_as!(
        Item,
        "SELECT id, text, created_at FROM items ORDER BY created_at DESC"
    )
    .fetch_all(pool)
    .await
    .map_err(|e| ServerFnError::ServerError(format!("Failed to fetch items: {}", e)))
}

pub async fn add_item_db(text: String) -> Result<(), ServerFnError> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    sqlx::query!(
        "INSERT INTO items (text, created_at) VALUES (?, ?)",
        text,
        Utc::now().naive_utc() // Store as NaiveDateTime in UTC
    )
    .execute(pool)
    .await
    .map_err(|e| ServerFnError::ServerError(format!("Failed to add item: {}", e)))?;
    Ok(())
}

pub async fn delete_item_db(id: i64) -> Result<(), ServerFnError> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    let result = sqlx::query!("DELETE FROM items WHERE id = ?", id)
        .execute(pool)
        .await
        .map_err(|e| ServerFnError::ServerError(format!("Failed to delete item: {}", e)))?;

    if result.rows_affected() == 0 {
        Err(ServerFnError::ServerError(format!("Item with id {} not found for deletion", id)))
    } else {
        Ok(())
    }
}
---

===== repo_src/app/src/error_template.rs =====
use leptos::*;
use leptos_meta::Title;
use http::status::StatusCode;

#[cfg(feature = "ssr")]
use leptos_axum::ResponseOptions;

#[component]
pub fn ErrorTemplate(
    #[prop(optional)] outside_errors: Option<Errors>,
    #[prop(optional)] errors: Option<RwSignal<Errors>>,
) -> impl IntoView {
    let errors = match outside_errors {
        Some(e) => create_rw_signal(e),
        None => match errors {
            Some(e) => e,
            None => panic!("No Errors found and ErrorTemplate expects errors!"),
        },
    };

    // Get the status code from the first error
    let first_error = errors.with_untracked(|e| e.iter().next().cloned());
    let status_code = first_error.as_ref().map_or(StatusCode::INTERNAL_SERVER_ERROR, |e| {
        e.status_code()
    });

    #[cfg(feature = "ssr")]
    {
        let response = use_context::<ResponseOptions>();
        if let Some(response) = response {
            response.set_status(status_code);
        }
    }

    view! {
        <Title text=move || format!("Error: {}", status_code.as_u16())/>
        <main class="container error-page">
            <h1>{move || format!("{}", status_code.as_u16())}</h1>
            <p>{move || status_code.canonical_reason().unwrap_or("Unknown Error")}</p>
            <h2>"Errors:"</h2>
            <For
                // a function that returns the items we're iterating over; a signal is fine
                each=errors
                // a unique key for each item
                key=|(key, _)| key.clone()
                // renders each item to a view
                children=move | (_, error)| {
                    let error_string = error.to_string();
                    let error_code= error.status_code();
                    view! {
                        <div class="error-detail">
                             <h3>{error_code.to_string()}</h3>
                             <p>{error_string}</p>
                        </div>
                    }
                }
            />
            <a href="/">"Go to Homepage"</a>
        </main>
    }
}
---

===== repo_src/app/src/lib.rs =====
use leptos::*;
pub mod app_component;
pub mod components;
pub mod error_template;
pub mod server_fns;
pub mod database; // For server-side logic, accessible in server_fns
// pub mod models; // if models are separate from shared, usually on server side

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    use app_component::AppComponent;
    use leptos_meta::provide_meta_context;

    _ = console_log::init_with_level(log::Level::Debug);
    console_error_panic_hook::set_once();

    leptos::mount_to_body(move || {
        provide_meta_context();
        view! { <AppComponent /> }
    });
}
---

===== repo_src/app/src/main.rs =====
#[cfg(feature = "ssr")]
#[tokio::main]
async fn main() {
    use axum::Router;
    use leptos::*;
    use leptos_axum::{generate_route_list, LeptosRoutes};
    use app::app_component::AppComponent; // Use the renamed component
    use app::error_template::ErrorTemplate;
    use tower_http::services::ServeDir;
    use app::database; // For migrations

    // Load .env file if present
    match dotenvy::dotenv() {
        Ok(path) => leptos::logging::log!("Loaded .env file from: {:?}", path),
        Err(_) => leptos::logging::log!("No .env file found, using environment variables directly or defaults."),
    }

    // Run migrations if the feature is enabled
    #[cfg(feature = "DATABASE_AUTO_MIGRATE")]
    {
        if let Err(e) = database::run_migrations().await {
            leptos::logging::error!("Failed to run database migrations: {:?}", e);
            // Depending on your error handling strategy, you might want to exit here
            // std::process::exit(1);
        }
    }


    let conf = get_configuration(None).await.unwrap();
    let leptos_options = conf.leptos_options;
    let addr = leptos_options.site_addr;
    let routes = generate_route_list(AppComponent);

    // build our application with a route
    let app = Router::new()
        .leptos_routes(&leptos_options, routes, AppComponent)
        .fallback_service(ServeDir::new(leptos_options.site_root.clone()))
        .with_state(leptos_options);

    leptos::logging::log!("listening on http://{}", &addr);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app.into_make_service()).await.unwrap();
}

#[cfg(not(feature = "ssr"))]
pub fn main() {
    // no client-side main function
    // all logic is handled by the lib.rs hydrate function called by wasm-bindgen
}
---

===== repo_src/app/src/server_fns.rs =====
use leptos::*;
use crate::database::{add_item_db, delete_item_db, get_all_items_db};
use shared::Item; // Assuming Item is in shared crate

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
pub struct GetItemsParams {}

#[server(GetItems, "/api")]
pub async fn get_items_server_fn(_params: GetItemsParams) -> Result<Vec<Item>, ServerFnError> {
    // In a real app, you might pass a DB connection pool via context
    // For simplicity here, database.rs functions might use a static pool
    get_all_items_db().await
}


#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
pub struct AddItemParams {
    pub text: String,
}
#[server(AddItem, "/api")]
pub async fn add_item_server_fn(params: AddItemParams) -> Result<(), ServerFnError> {
    if params.text.trim().is_empty() {
        return Err(ServerFnError::Args("Item text cannot be empty".into()));
    }
    if params.text.len() > 100 {
         return Err(ServerFnError::Args("Item text too long (max 100 chars)".into()));
    }
    add_item_db(params.text).await
}


#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
pub struct DeleteItemParams {
    pub id: i64,
}
#[server(DeleteItem, "/api")]
pub async fn delete_item_server_fn(params: DeleteItemParams) -> Result<(), ServerFnError> {
    delete_item_db(params.id).await
}

// Ensure the server_fn_type_aliases macro is called to generate the necessary type aliases
// This should be done once, typically in lib.rs or main.rs if it's a binary-only crate.
// However, cargo-leptos handles this under the hood when it sees #[server] macros.
// So, explicitly calling it might not be needed if cargo-leptos is correctly configured.
// If you encounter "function not found" errors for server functions on client side, ensure
// that the code generation step (usually handled by cargo-leptos) is working.
// For example, in your lib.rs:
// #[cfg(feature = "ssr")]
// pub fn register_server_functions() {
//    _ = GetItems::register_explicit();
//    _ = AddItem::register_explicit();
//    _ = DeleteItem::register_explicit();
// }
// Then call this function in your main server startup.
// Leptos 0.6+ and cargo-leptos usually make this more seamless.
---

===== repo_src/app/style/main.css =====
/* Basic Reset/Defaults */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
    line-height: 1.6;
    color: #333;
    background-color: #f4f7f6;
    padding: 20px;
    display: flex;
    justify-content: center;
}

.container {
    width: 100%;
    max-width: 700px;
    background-color: #fff;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #2c3e50;
    margin-bottom: 20px;
    text-align: center;
    font-size: 2em;
}

h2 {
    color: #34495e;
    margin-top: 20px;
    margin-bottom: 15px;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 5px;
    font-size: 1.5em;
}

.card {
    background-color: #ffffff; /* Or a slightly off-white for depth */
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 25px;
}


/* Form Styling */
.item-form div {
    margin-bottom: 15px;
}

.item-form label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
}

.item-form input[type="text"] {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1em;
}

.item-form input[type="text"]:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    outline: none;
}

.button-primary {
    background-color: #007bff;
    color: white;
    padding: 10px 18px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.2s ease-in-out;
}

.button-primary:hover {
    background-color: #0056b3;
}

.button-primary:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}


/* Item List Styling */
.item-list {
    list-style-type: none;
}

.item-list .item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #eee;
    transition: background-color 0.15s ease-in-out;
}

.item-list .item:last-child {
    border-bottom: none;
}

.item-list .item:hover {
    background-color: #f9f9f9;
}

.item-list .item-text {
    flex-grow: 1;
    margin-right: 10px;
    word-break: break-word;
}

.item-list .item-date {
    font-size: 0.8em;
    color: #777;
    margin-right: 15px;
    min-width: 120px; /* Adjust as needed */
    text-align: right;
}


.item-delete {
    background-color: #e74c3c;
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background-color 0.2s ease-in-out;
}

.item-delete:hover {
    background-color: #c0392b;
}

.loading-indicator {
    text-align: center;
    color: #007bff;
    padding: 10px;
    font-style: italic;
}

/* Error Page */
.error-page {
    text-align: center;
}
.error-page h1 {
    font-size: 3em;
    color: #e74c3c;
}
.error-page .error-detail {
    margin-top: 15px;
    padding: 10px;
    background-color: #fdd;
    border: 1px solid #fbb;
    border-radius: 4px;
}
.error-page a {
    display: inline-block;
    margin-top: 20px;
    color: #007bff;
    text-decoration: none;
}
.error-page a:hover {
    text-decoration: underline;
}
---

===== repo_src/shared/Cargo.toml =====
[package]
name = "shared"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
chrono = { version = "0.4", features = ["serde"] } # For timestamps if needed directly in shared DTOs

# Required by Leptos if these types are passed to server functions or used in signals directly
# and need to be (de)serialized across wasm/server boundary by Leptos itself.
# For simple data DTOs, serde is usually enough.
leptos = { version = "0.6", default-features = false, optional = true } # Keep optional if not always needed by all shared types

[features]
# This feature can be used by the app crate to enable leptos-specific derives if needed
# for some shared types.
with_leptos = ["dep:leptos"]
---

===== repo_src/shared/src/lib.rs =====
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, NaiveDateTime};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Item {
    pub id: i64,
    pub text: String,
    // Store as NaiveDateTime if your DB doesn't handle timezone well, convert to DateTime<Utc> in app logic
    // Or, ensure DB stores with timezone and read as DateTime<Utc>
    // For SQLite, it's often simpler to store as TEXT (ISO8601) or INTEGER (unix timestamp)
    // and parse. SQLx handles NaiveDateTime to TEXT for SQLite by default.
    pub created_at: NaiveDateTime, // Example: 2023-10-26 09:30:00
}

// If you need to pass DateTime<Utc> directly from server fns and deserialize on client:
// #[derive(Clone, Debug, Serialize, Deserialize)]
// pub struct Item {
//     pub id: i64,
//     pub text: String,
//     #[serde(with = "chrono::serde::ts_milliseconds")] // Example for serde with chrono
//     pub created_at: DateTime<Utc>,
// }
---
This completes the generation of the Rust full-stack template.
You can now:
1.  Save these files into their respective paths.
2.  Ensure you have Rust, `cargo-leptos`, `sqlx-cli` (optional), and the `wasm32-unknown-unknown` target installed.
3.  Copy `.env.example` to `.env`.
4.  Run `sqlx migrate run --source repo_src/app/migrations` (or rely on auto-migration).
5.  Run `cargo leptos watch` to start the development server.

The application should be accessible at `http://127.0.0.1:3000`. You'll be able to add and delete items, with data persisted in the `target/dev.db` SQLite file.

The `README.md`, `README.testing.md`, and `docs/feature_flow.md` provide guidance on using and extending this template.