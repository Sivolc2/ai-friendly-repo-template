# Rust Full-Stack Web Application Template (Leptos + Axum + SQLx)

This repository provides a template for building full-stack web applications in Rust using the Leptos framework, with Axum for the server-side backend (managed via `cargo-leptos`) and SQLx for asynchronous, compile-time checked SQL database interaction (using SQLite by default).

It's designed to be AI-friendly, encouraging clear structure, good documentation, and a straightforward development workflow.

## Features

*   **Full-Stack Rust:** Write both your frontend and backend logic in Rust.
*   **Leptos Framework (v0.6):** A modern, ergonomic Rust framework for building reactive web UIs.
*   **Axum Backend:** Integrated via `cargo-leptos` for serving the application and handling API requests (through Leptos server functions).
*   **SQLx & SQLite:** Asynchronous SQL toolkit with compile-time query checking. SQLite is used for easy setup.
*   **Hot Reloading:** `cargo leptos watch` provides a fast development loop.
*   **Workspace Structure:** Clear separation of concerns with `frontend`, `backend`, and `shared` crates.
*   **Basic CRUD Example:** A simple item list manager demonstrates database interaction and frontend reactivity.
*   **Environment Configuration:** Uses `.env` files for managing settings like database URLs.
*   **Clear Documentation:** Guidelines for setup, development, and testing.

## Project Structure

```
.
├── example_env_file.sh  # Example environment variables (copy to .env)
├── .gitignore
├── Cargo.toml           # Workspace root with Leptos configuration
├── README.md            # This file
├── README.testing.md    # Testing guidelines
├── rust-toolchain.toml  # Specifies Rust toolchain version
├── docs/
│   └── guides/
│       └── init.md      # Complete template creation guide
└── repo_src/
    ├── frontend/        # Leptos frontend application
    │   ├── Cargo.toml
    │   ├── index.html     # Main HTML file for Leptos
    │   ├── migrations/    # SQLx migrations (e.g., 0001_create_items_table.sql)
    │   ├── public/        # Static assets directory
    │   ├── src/           # Frontend source code
    │   │   ├── app_component.rs
    │   │   ├── components/
    │   │   ├── database.rs      # Server-side database functions (SSR feature)
    │   │   ├── error_template.rs
    │   │   ├── lib.rs
    │   │   └── server_fns.rs    # Leptos server functions
    │   └── style/
    │       └── main.css
    ├── backend/         # Axum server binary
    │   ├── Cargo.toml
    │   └── src/
    │       └── main.rs    # Server startup and configuration
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
    cd <repository-name> # Stay in the workspace root
    ```

2.  **Set up environment variables:**
    Ensure you are in the workspace root. Copy `example_env_file.sh` contents to a new file named `.env` in the workspace root.
    Remove the `export ` prefixes from each line in the `.env` file.
    ```bash
    # Example:
    # cp example_env_file.sh .env
    # Then edit .env to remove 'export ' from lines, or use:
    # sed -i'.bak' 's/export //g' .env  # On macOS (creates .env.bak)
    # sed -i 's/export //g' .env       # On Linux
    ```
    Your `.env` file (in the workspace root) should look like:
    ```
    DATABASE_URL="sqlite:./target/dev.db?mode=rwc"
    RUST_BACKTRACE=0
    # LEPTOS_... variables if needed
    ```

3.  **Build the application (from workspace root):**
    ```bash
    cargo leptos build
    ```

4.  **Run the development server (from workspace root):**
    ```bash
    cargo leptos watch
    ```
    This command will build the application, start a development server, and watch for file changes to enable hot reloading.
    Open your browser to `http://127.0.0.1:3000` (or the address shown in the terminal).
    The `DATABASE_URL` path `./target/dev.db` will be relative to the workspace root.

## Development Workflow

*   **Frontend Logic:** Modify files in `repo_src/frontend/src/` for UI components and client-side logic.
*   **Server Functions:** Define backend API endpoints in `repo_src/frontend/src/server_fns.rs`.
*   **Database Interactions:** Manage database logic in `repo_src/frontend/src/database.rs` (compiled only with SSR feature).
*   **Backend Configuration:** Server startup and configuration in `repo_src/backend/src/main.rs`.
*   **Shared Types:** Add shared data structures in `repo_src/shared/src/lib.rs`.
*   **Styling:** Add CSS to `repo_src/frontend/style/main.css`. Ensure it's linked in `repo_src/frontend/index.html`.
*   **Adding Dependencies:**
    *   For the frontend: `cargo add <crate_name> -p frontend`
    *   For the backend: `cargo add <crate_name> -p backend`
    *   For shared types: `cargo add <crate_name> -p shared`

Refer to `docs/guides/init.md` for the complete template creation guide and feature development workflow.

## Database Seeding

The application includes automatic database seeding to populate empty databases with initial data:

### **Automatic Seeding**
- **When:** Runs automatically after migrations during app startup
- **Environment:** Only in development (`LEPTOS_ENV=DEV`, which is the default)
- **Condition:** Only seeds if the items table is empty
- **Initial Data:** Creates three sample items: "Buy groceries", "Read a book", "Learn Leptos"

### **Manual Seeding Commands**
You can also seed the database manually using command-line options:

```bash
# Seed database only if empty (same as automatic behavior)
./target/release/backend --seed

# Force seed database (adds items regardless of existing data)  
./target/release/backend --force-seed

# Show help for available commands
./target/release/backend --help
```

### **Production Behavior**
- Seeding is **disabled** in production environments (`LEPTOS_ENV=PROD`)
- Migrations still run automatically in production
- Use manual seeding commands if needed in production

## Building for Production
(From the workspace root)
```bash
cargo leptos build --release
```
This will create an optimized build:
- Server binary: `target/release/backend` (or `backend.exe` on Windows).
- Frontend assets: `target/site/` (WASM, JS glue, CSS).

## Running in Production

After building, you can run the server binary:
(From the workspace root)
```bash
./target/release/backend
```
Ensure your production environment has the necessary environment variables set (e.g., `DATABASE_URL`).

## Testing

See `README.testing.md` for guidelines on testing different parts of the application.
To run tests:
```bash
cargo test --workspace
```

## Template Status

✅ **Basic Template Complete:** The template compiles and builds successfully  
✅ **Workspace Configuration:** Leptos integrated at workspace level with proper feature separation  
✅ **Runtime Fixed:** Server starts without panics, proper LocalSet integration  
✅ **Database Integration:** Full database initialization, seeding, and testing implemented  
📝 **Next Steps:** Implement the full CRUD functionality in frontend components

## Current Implementation

The template currently includes:
- ✅ Workspace structure with `frontend`, `backend`, and `shared` crates
- ✅ Basic Leptos app component with "Hello, World!" placeholder
- ✅ Database layer with SQLite setup, migrations, and seeding
- ✅ Server function infrastructure (placeholder implementations)
- ✅ Comprehensive testing framework for database and server functions
- ✅ Component structure (item form and list placeholders)  
- ✅ CSS styling framework
- ✅ Build system configuration
- ✅ Proper feature separation (hydrate for client, ssr for server)
- ✅ Working development server with hot reload

**Next Development Steps:**
1. Implement full CRUD functionality in components
2. Connect frontend components to server functions
3. Add proper error handling and validation
4. Implement database operations for items

## Architecture Notes

**Feature Separation:**
- **Frontend crate:** Uses `hydrate` feature for client-side builds (WASM), `ssr` feature for server-side compilation
- **Backend crate:** Depends on frontend with `ssr` feature only, no WASM dependencies
- **Shared crate:** Pure Rust types, no framework dependencies

**Build Process:**
- `cargo leptos build` builds both client (WASM) and server binaries
- Client build: `frontend` crate with `hydrate` features → WASM bundle
- Server build: `backend` crate pulling `frontend` with `ssr` features → native binary

## Troubleshooting

**Build Issues:**
- Ensure `cargo-leptos` is installed: `cargo install cargo-leptos`
- Ensure wasm target is installed: `rustup target add wasm32-unknown-unknown`
- Check that environment variables are set correctly

**Database Issues:**
- Verify `DATABASE_URL` is set in `.env` file
- Check that the target directory exists for SQLite file creation
- Run migrations manually if auto-migration fails: `sqlx migrate run --source repo_src/frontend/migrations`
- Use manual seeding commands if needed: `./target/release/backend --seed`

**Runtime Issues:**
- If you see `spawn_local` errors, ensure `leptos_axum` uses default features in `backend/Cargo.toml`
- For WASM compilation errors on server, verify `frontend` dependency has `default-features = false` in `backend/Cargo.toml`

## License

This template is provided as-is for educational and development purposes.