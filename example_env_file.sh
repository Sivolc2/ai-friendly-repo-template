# Example environment variables
# Copy this file to .env and fill in your values.

# Database URL for SQLx
# For SQLite, this can be a file path.
# Example: DATABASE_URL="sqlite:mydatabase.db?mode=rwc" (rwc = read/write/create)
# Ensure the directory exists if it's a relative path, or use an absolute path.
export DATABASE_URL="sqlite:./target/dev.db?mode=rwc"
export RUST_BACKTRACE=0
export LEPTOS_ENV=DEV

# Leptos specific environment variables (optional, defaults are usually fine)
# export LEPTOS_OUTPUT_NAME="my_leptos_app"
# export LEPTOS_SITE_ROOT="target/site"
# export LEPTOS_SITE_PKG_DIR="pkg"
# export LEPTOS_SITE_ADDR="127.0.0.1:3000"
# export LEPTOS_RELOAD_PORT="3001" 