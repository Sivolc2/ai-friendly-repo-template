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
    let database_url = if cfg!(test) {
        // For tests, prioritize a specific test env var, then TEST_DATABASE_URL, then fallback to in-memory
        env::var("TEST_DATABASE_URL_FOR_SERVER_FN_TESTS")
            .or_else(|_| env::var("TEST_DATABASE_URL"))
            .unwrap_or_else(|_| {
                leptos::logging::warn!("[DB LOG Init - Test Mode] Neither TEST_DATABASE_URL_FOR_SERVER_FN_TESTS nor TEST_DATABASE_URL set, defaulting POOL init to sqlite::memory:");
                "sqlite::memory:".to_string()
            })
    } else {
        env::var("DATABASE_URL")
            .map_err(|e| sqlx::Error::Configuration(format!("DATABASE_URL not set: {}",e).into()))?
    };
    
    leptos::logging::log!("[DB LOG Init] Initializing pool with URL: {}", database_url);
    SqlitePoolOptions::new()
        .max_connections(if cfg!(test) { 1 } else { 5 }) // Fewer connections for tests
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
    let test_db_url = env::var("TEST_DATABASE_URL").unwrap_or_else(|_| {
        leptos::logging::log!("[DB LOG get_db_pool_test] TEST_DATABASE_URL not set, using sqlite::memory:");
        "sqlite::memory:".to_string()
    });
    SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&test_db_url)
        .await
}

// Called from backend/main.rs on server startup if DATABASE_AUTO_MIGRATE feature is enabled
#[cfg(feature = "DATABASE_AUTO_MIGRATE")]
pub async fn run_migrations() -> Result<(), sqlx::Error> {
    leptos::logging::log!("[DB LOG] Attempting to run migrations from frontend::database::run_migrations...");
    let pool = get_db_pool().await?;
    leptos::logging::log!("[DB LOG] Acquired DB pool for migrations. Migration source path: ./migrations (relative to frontend crate).");

    // Path is relative to CARGO_MANIFEST_DIR of the crate where this is compiled,
    // which is `frontend` crate. So, `frontend/migrations`.
    sqlx::migrate!("./migrations")
        .run(pool)
        .await?;
    leptos::logging::log!("[DB LOG] Database migrations applied successfully from run_migrations.");
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

pub async fn seed_database() -> Result<(), String> {
    leptos::logging::log!("[DB LOG] Checking if database seeding is required...");
    let pool = get_db_pool().await.map_err(|e| format!("DB Pool error for seeding: {}", e))?;

    // Check if items table is empty
    let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM items")
        .fetch_one(pool)
        .await
        .map_err(|e| format!("Failed to count items for seeding: {}", e))?;

    if count == 0 {
        leptos::logging::log!("[DB LOG] Items table is empty. Seeding initial data...");
        let initial_items = vec![
            "Buy groceries",
            "Read a book",
            "Learn Leptos",
        ];
        for item_text in initial_items {
            // Use existing add_item_db which handles created_at
            // Note: add_item_db itself gets a new pool. For seeding, it might be more efficient
            // to have an add_item_core(text, pool) and use the pool obtained above.
            // However, for a few items, this is fine.
            if let Err(e) = add_item_db(item_text.to_string()).await {
                 // Log error but continue seeding other items if possible
                leptos::logging::error!("[DB LOG] Error seeding item '{}': {}", item_text, e);
            }
        }
        leptos::logging::log!("[DB LOG] ✅ Database seeding completed successfully!");
    } else {
        leptos::logging::log!("[DB LOG] Database already has data ({} items). Skipping seeding.", count);
    }
    Ok(())
}

// Force seed the database regardless of existing data (useful for testing or manual seeding)
pub async fn force_seed_database() -> Result<(), String> {
    leptos::logging::log!("[DB LOG] Force seeding database (will add items regardless of existing data)...");
    let initial_items = vec![
        "Buy groceries",
        "Read a book", 
        "Learn Leptos",
    ];
    for item_text in initial_items {
        if let Err(e) = add_item_db(item_text.to_string()).await {
            leptos::logging::error!("[DB LOG] Error force seeding item '{}': {}", item_text, e);
        }
    }
    leptos::logging::log!("[DB LOG] ✅ Force database seeding completed!");
    Ok(())
}

#[cfg(all(test, feature = "ssr"))] // Ensure ssr features are active for tests needing DB
mod tests {
    use super::*; // To access get_db_pool_test, add_item_db etc.
    use sqlx::Row;

    // Helper to setup an in-memory test DB and run migrations
    async fn setup_test_db_with_migrations() -> Result<SqlitePool, sqlx::Error> {
        // get_db_pool_test() returns a new in-memory pool or one based on TEST_DATABASE_URL
        let pool = get_db_pool_test().await?;
        
        // Run migrations on this specific pool
        // The path is relative to CARGO_MANIFEST_DIR of `frontend` crate.
        sqlx::migrate!("./migrations")
            .run(&pool)
            .await
            .expect("Failed to run migrations on test DB");
        Ok(pool)
    }

    #[tokio::test]
    async fn test_migrations_on_test_db() {
        let pool_result = setup_test_db_with_migrations().await;
        assert!(pool_result.is_ok(), "Migrations failed on test DB setup: {:?}", pool_result.err());
        
        let pool = pool_result.unwrap();
        let row = sqlx::query("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
            .fetch_optional(&pool)
            .await
            .expect("Query to check table existence failed");
        assert!(row.is_some(), "items table not found after migrations");
    }

    #[tokio::test]
    async fn test_add_item_db_via_direct_sql_with_pool() {
        let pool = setup_test_db_with_migrations().await.unwrap();
        
        let text = "Test item for direct pool".to_string();
        let now_utc_naive = Utc::now().naive_utc();
        let query_result = sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
            .bind(text.clone())
            .bind(now_utc_naive)
            .execute(&pool)
            .await;
        assert!(query_result.is_ok(), "Insert failed: {:?}", query_result.err());

        let item_row = sqlx::query("SELECT text FROM items WHERE text = ?")
            .bind(text)
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(item_row.get::<String, _>("text"), "Test item for direct pool");
    }

    // Helper DB functions for testing that accept a pool
    // These are effectively what the main db functions should be like if refactored for testability
    async fn get_all_items_db_with_pool(pool: &SqlitePool) -> Result<Vec<Item>, String> {
        let rows = sqlx::query("SELECT id, text, created_at FROM items ORDER BY created_at DESC")
            .fetch_all(pool)
            .await
            .map_err(|e| format!("Failed to fetch items: {}", e))?;
        Ok(rows.into_iter().map(|row| Item {
            id: row.get("id"), text: row.get("text"), created_at: row.get("created_at")
        }).collect())
    }
    async fn delete_item_db_with_pool(id: i64, pool: &SqlitePool) -> Result<(), String> {
        let result = sqlx::query("DELETE FROM items WHERE id = ?")
            .bind(id)
            .execute(pool)
            .await
            .map_err(|e| format!("Failed to delete item: {}", e))?;
        if result.rows_affected() == 0 {
            Err(format!("Item with id {} not found", id))
        } else { Ok(()) }
    }

    #[tokio::test]
    async fn test_get_all_items_db_with_pool_helper() {
        let pool = setup_test_db_with_migrations().await.unwrap();
        
        sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
            .bind("Item 1".to_string()).bind(Utc::now().naive_utc())
            .execute(&pool).await.unwrap();
        sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
            .bind("Item 2".to_string()).bind(Utc::now().naive_utc())
            .execute(&pool).await.unwrap();

        let items = get_all_items_db_with_pool(&pool).await.unwrap();
        assert_eq!(items.len(), 2);
        assert!(items.iter().any(|item| item.text == "Item 1"));
        assert!(items.iter().any(|item| item.text == "Item 2"));
    }

    #[tokio::test]
    async fn test_delete_item_db_with_pool_helper() {
        let pool = setup_test_db_with_migrations().await.unwrap();
        
        let text = "Item to delete".to_string();
        sqlx::query("INSERT INTO items (text, created_at) VALUES (?, ?)")
            .bind(text.clone()).bind(Utc::now().naive_utc())
            .execute(&pool).await.unwrap();
        
        let item_id: i64 = sqlx::query_scalar("SELECT id FROM items WHERE text = ?")
            .bind(text).fetch_one(&pool).await.unwrap();

        let delete_result = delete_item_db_with_pool(item_id, &pool).await;
        assert!(delete_result.is_ok());

        let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM items WHERE id = ?")
            .bind(item_id).fetch_one(&pool).await.unwrap();
        assert_eq!(count, 0);
    }
} 