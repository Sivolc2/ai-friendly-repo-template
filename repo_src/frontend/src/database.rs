// This entire module is only compiled when the "ssr" feature is enabled.
#![cfg(feature = "ssr")]

use sqlx::{sqlite::SqlitePoolOptions, SqlitePool, Row};
use std::env;
use std::sync::OnceLock;
use shared::Item;
use chrono::{Utc, NaiveDateTime};

// Global static pool, initialized once.
static POOL: OnceLock<SqlitePool> = OnceLock::new();

async fn init_pool() -> Result<SqlitePool, sqlx::Error> {
    let database_url = env::var("DATABASE_URL")
        .map_err(|_| sqlx::Error::Configuration("DATABASE_URL not set".into()))?;
    
    SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
}

pub async fn get_db_pool() -> Result<&'static SqlitePool, sqlx::Error> {
    if POOL.get().is_none() {
        // Ensure dotenvy is called before first pool access if .env is used for DATABASE_URL
        // dotenvy::dotenv().ok(); // This should ideally be called once at app startup in backend/main.rs
        let pool = init_pool().await?;
        POOL.set(pool).map_err(|_| sqlx::Error::PoolClosed)?;
    }
    Ok(POOL.get().unwrap())
}

// Separate function for test database pool if needed (ensure TEST_DATABASE_URL is set for tests)
pub async fn get_db_pool_test() -> Result<SqlitePool, sqlx::Error> {
    let test_db_url = env::var("TEST_DATABASE_URL").unwrap_or_else(|_| "sqlite::memory:".to_string());
    SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&test_db_url)
        .await
}

// Called from backend/main.rs on server startup if DATABASE_AUTO_MIGRATE feature is enabled
#[cfg(feature = "DATABASE_AUTO_MIGRATE")]
pub async fn run_migrations() -> Result<(), sqlx::Error> {
    leptos::logging::log!("Running database migrations (from frontend::database)...");
    let pool = get_db_pool().await?;
    // Path is relative to CARGO_MANIFEST_DIR of the crate where this is compiled,
    // which is `frontend` crate. So, `frontend/migrations`.
    sqlx::migrate!("./migrations")
        .run(pool)
        .await?;
    leptos::logging::log!("Database migrations completed.");
    Ok(())
}

// --- CRUD Operations ---
// These now return Result<_, String> for errors.

pub async fn get_all_items_db() -> Result<Vec<Item>, String> {
    let pool = get_db_pool().await.map_err(|e| format!("DB Pool error: {}", e))?;
    
    let rows = sqlx::query("SELECT id, text, created_at FROM items ORDER BY created_at DESC")
        .fetch_all(pool)
        .await
        .map_err(|e| format!("Failed to fetch items: {}", e))?;

    let items = rows.into_iter().map(|row| {
        let id: i64 = row.get("id");
        let text: String = row.get("text");
        // SQLx can parse recognized TEXT formats (ISO8601 subset) into NaiveDateTime directly
        // For SQLite default (TEXT as YYYY-MM-DD HH:MM:SS), this should work.
        let created_at: NaiveDateTime = row.get("created_at");
        Item { id, text, created_at }
    }).collect();

    Ok(items)
}

pub async fn add_item_db(text: String) -> Result<(), String> {
    let pool = get_db_pool().await.map_err(|e| format!("DB Pool error: {}", e))?;
    
    // Using NaiveDateTime directly with SQLx for SQLite will store it as TEXT in 'YYYY-MM-DD HH:MM:SS' format.
    let now_utc_naive = Utc::now().naive_utc();
    
    sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
        .bind(text)
        .bind(now_utc_naive) // SQLx handles NaiveDateTime to TEXT
        .execute(pool)
        .await
        .map_err(|e| format!("Failed to add item: {}", e))?;
    
    Ok(())
}

pub async fn delete_item_db(id: i64) -> Result<(), String> {
    let pool = get_db_pool().await.map_err(|e| format!("DB Pool error: {}", e))?;
    
    let result = sqlx::query("DELETE FROM items WHERE id = ?")
        .bind(id)
        .execute(pool)
        .await
        .map_err(|e| format!("Failed to delete item: {}", e))?;

    if result.rows_affected() == 0 {
        Err(format!("Item with id {} not found for deletion", id))
    } else {
        Ok(())
    }
} 