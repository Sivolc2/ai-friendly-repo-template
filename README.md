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
├── example_env_file.sh  # Example environment variables (copy to .env)
├── .gitignore
├── Cargo.toml           # Workspace root
├── README.md            # This file
├── README.testing.md    # Testing guidelines
├── rust-toolchain.toml  # Specifies Rust toolchain version
├── docs/
│   └── guides/
│       └── init.md      # Complete template creation guide
└── repo_src/
    ├── app/             # Main Leptos application (FE & BE logic)
    │   ├── Cargo.toml
    │   ├── index.html     # Main HTML file for Leptos
    │   ├── migrations/    # SQLx migrations (e.g., 0001_create_items_table.sql)
    │   ├── public/        # Static assets directory
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
    Copy `example_env_file.sh` contents to `.env` (remove the `export` commands):
    ```bash
    cp example_env_file.sh .env
    sed -i '' 's/export //g' .env  # On macOS
    # or sed -i 's/export //g' .env  # On Linux
    ```

3.  **Build the application:**
    ```bash
    cd repo_src/app
    cargo leptos build
    ```

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

Refer to `docs/guides/init.md` for the complete template creation guide and feature development workflow.

## Building for Production

```bash
cd repo_src/app
cargo leptos build --release
```
This will create an optimized build in the `target/release` directory for the server binary and `target/site` for the frontend assets (WASM, JS glue, CSS).

## Running in Production

After building, you can run the server binary:
```bash
./target/release/app  # From the app directory
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
🚧 **Feature Implementation:** Basic app structure is ready for feature development  
📝 **Next Steps:** Implement the full CRUD functionality

## Current Implementation

The template currently includes:
- ✅ Workspace structure with `app` and `shared` crates
- ✅ Basic Leptos app component with "Hello, World!" placeholder
- ✅ Database layer with SQLite setup and migrations
- ✅ Server function infrastructure (placeholder implementations)
- ✅ Component structure (item form and list placeholders)  
- ✅ CSS styling framework
- ✅ Build system configuration

**Next Development Steps:**
1. Implement full CRUD functionality in components
2. Connect frontend components to server functions
3. Add proper error handling and validation
4. Implement database operations for items

## Troubleshooting

**Build Issues:**
- Ensure `cargo-leptos` is installed: `cargo install cargo-leptos`
- Ensure wasm target is installed: `rustup target add wasm32-unknown-unknown`
- Check that environment variables are set correctly

**Database Issues:**
- Verify `DATABASE_URL` is set in `.env` file
- Check that the target directory exists for SQLite file creation
- Run migrations manually if auto-migration fails: `sqlx migrate run --source repo_src/app/migrations`

## License

This template is provided as-is for educational and development purposes. 