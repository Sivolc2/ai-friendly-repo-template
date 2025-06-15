use sqlx::{sqlite::SqlitePoolOptions, SqlitePool, Row};
use std::env;
use std::sync::OnceLock;
use leptos::ServerFnError;
use shared::Item; // Assuming Item is in shared crate
use chrono::{Utc, NaiveDateTime};

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


// --- CRUD Operations using runtime queries ---

pub async fn get_all_items_db() -> Result<Vec<Item>, ServerFnError<String>> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    
    let rows = sqlx::query("SELECT id, text, created_at FROM items ORDER BY created_at DESC")
        .fetch_all(pool)
        .await
        .map_err(|e| ServerFnError::ServerError(format!("Failed to fetch items: {}", e)))?;

    let items = rows.into_iter().map(|row| {
        let id: i64 = row.get("id");
        let text: String = row.get("text");
        let created_at_str: String = row.get("created_at");
        
        // Parse the timestamp string to NaiveDateTime
        let created_at = NaiveDateTime::parse_from_str(&created_at_str, "%Y-%m-%d %H:%M:%S")
            .unwrap_or_else(|_| Utc::now().naive_utc());
        
        Item { id, text, created_at }
    }).collect();

    Ok(items)
}

pub async fn add_item_db(text: String) -> Result<(), ServerFnError<String>> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    
    let now = Utc::now().naive_utc().format("%Y-%m-%d %H:%M:%S").to_string();
    
    sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
        .bind(text)
        .bind(now)
        .execute(pool)
        .await
        .map_err(|e| ServerFnError::ServerError(format!("Failed to add item: {}", e)))?;
    
    Ok(())
}

pub async fn delete_item_db(id: i64) -> Result<(), ServerFnError<String>> {
    let pool = get_db_pool().await.map_err(|e| ServerFnError::ServerError(format!("DB Pool error: {}", e)))?;
    
    let result = sqlx::query("DELETE FROM items WHERE id = ?")
        .bind(id)
        .execute(pool)
        .await
        .map_err(|e| ServerFnError::ServerError(format!("Failed to delete item: {}", e)))?;

    if result.rows_affected() == 0 {
        Err(ServerFnError::ServerError(format!("Item with id {} not found for deletion", id)))
    } else {
        Ok(())
    }
} 