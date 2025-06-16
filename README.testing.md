# Testing Guidelines

Testing a full-stack Leptos application involves several layers. Here's a guide to approaching testing in this template:

## 1. Unit Tests for Business Logic

*   **Location:** Alongside your modules (e.g., in `repo_src/frontend/src/database.rs` or other logic modules).
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

## 2. Testing Server Functions and Database Logic

Leptos server functions encapsulate backend logic. Direct database logic resides in `repo_src/frontend/src/database.rs`.

*   **Location:**
    *   Server Function Tests: `repo_src/frontend/src/server_fns.rs` in a `#[cfg(test)] mod tests`.
    *   Database Logic Tests: `repo_src/frontend/src/database.rs` in a `#[cfg(test)] mod tests`.
*   **Strategy:**
    *   **Test Database:** Use an in-memory SQLite database for tests to ensure isolation and speed. The `database::get_db_pool_test()` function (which defaults to `sqlite::memory:`) is provided for this.
    *   **Migrations:** Each test or test suite run that interacts with the database must first run migrations on the test database instance.
    *   **Server Functions:**
        *   Create a Leptos runtime (`create_runtime()`).
        *   The current server functions in `server_fns.rs` call database access functions (e.g., `add_item_db`) which internally use a global `database::POOL`. To make these testable with an isolated in-memory database:
            *   The `database::init_pool()` function has been modified to check `cfg!(test)`. In test mode, it uses the `TEST_DATABASE_URL_FOR_SERVER_FN_TESTS` or `TEST_DATABASE_URL` environment variable (defaulting to `sqlite::memory:`).
            *   Server function tests can set one of these environment variables to `sqlite::memory:`. Then, when migrations are run using `get_db_pool_test()` (which also respects these variables in test mode) and server functions are subsequently called, they will all interact with the same in-memory database.
        *   **Alternative/Recommended Refactoring:** For more robust testing, refactor core database logic functions (e.g., create `add_item_core(&SqlitePool, ...)`) to accept an `&sqlx::SqlitePool`. Server functions could then retrieve a pool (e.g., via `leptos::use_context()`, which can be mocked in tests) and pass it to these core functions. This improves dependency injection and test isolation.
        *   Call the server function directly. Assert the `Result`.
    *   **Direct Database Functions:**
        *   Obtain a test pool using `database::get_db_pool_test().await?`.
        *   Run migrations: `sqlx::migrate!("./migrations").run(&pool).await?`. The path `./migrations` is relative to the `frontend` crate root.
        *   Call the database functions using this test pool.
            *   *Note:* The main database functions (`add_item_db`, etc.) use a global static pool. For direct unit testing of their logic with a specific test pool, either:
                1.  Refactor them to accept `&SqlitePool` as a parameter (recommended). The tests in `database.rs` include helper functions like `get_all_items_db_with_pool` that demonstrate this pattern.
                2.  Ensure the global pool mechanism (`database::init_pool`) is configured for a test DB during tests (as done for server function tests above).

**Example Test Setup in `database.rs`:**
```rust
// In repo_src/frontend/src/database.rs
#[cfg(all(test, feature = "ssr"))]
mod tests {
    use super::*; // To access database functions and get_db_pool_test
    use sqlx::Row; // For accessing row data

    // Helper to setup an in-memory test DB and run migrations
    async fn setup_test_db_with_migrations() -> Result<sqlx::SqlitePool, sqlx::Error> {
        let pool = get_db_pool_test().await?; // Uses sqlite::memory: by default
        // Path relative to `frontend` crate's Cargo.toml
        sqlx::migrate!("./migrations")
            .run(&pool)
            .await
            .expect("Failed to run migrations on test DB");
        Ok(pool)
    }

    #[tokio::test]
    async fn test_add_and_get_item_with_pool() {
        let pool = setup_test_db_with_migrations().await.unwrap();
        
        // Example of directly using SQL with the test pool
        let item_text = "My Test Item".to_string();
        let now_utc_naive = chrono::Utc::now().naive_utc();
        sqlx::query("INSERT INTO items (text, created_at) VALUES ($1, $2)")
            .bind(item_text.clone())
            .bind(now_utc_naive)
            .execute(&pool).await.unwrap();

        // Use a helper that takes the pool for fetching
        let items = get_all_items_db_with_pool(&pool).await.unwrap();
        assert_eq!(items.len(), 1);
        assert_eq!(items[0].text, item_text);
    }
    
    // Placeholder for actual database functions that would take a pool
    async fn get_all_items_db_with_pool(pool: &sqlx::SqlitePool) -> Result<Vec<shared::Item>, String> {
        let rows = sqlx::query("SELECT id, text, created_at FROM items ORDER BY created_at DESC")
            .fetch_all(pool)
            .await
            .map_err(|e| format!("Failed to fetch items: {}", e))?;
        Ok(rows.into_iter().map(|row| shared::Item {
            id: row.get("id"), text: row.get("text"), created_at: row.get("created_at")
        }).collect())
    }
}
```

**Testing Server Functions (Simplified approach used in `server_fns.rs` tests):**

The tests for server functions in `repo_src/frontend/src/server_fns.rs` are set up to use an in-memory database by:
1.  Modifying `database::init_pool()` to use `TEST_DATABASE_URL_FOR_SERVER_FN_TESTS` or `TEST_DATABASE_URL` (defaulting to `sqlite::memory:`) when `cfg!(test)` is true.
2.  The test function `test_add_get_delete_item_server_fns` temporarily sets `TEST_DATABASE_URL_FOR_SERVER_FN_TESTS` to `sqlite::memory:`.
3.  It then calls `database::get_db_pool_test().await` (which will use the in-memory URL) to get a pool and runs migrations on it.
4.  Subsequent calls to server functions (like `add_item()`, `get_items()`) will internally call `database::get_db_pool()`, which, due to the modified `init_pool()` and the environment variable, will also connect to the same in-memory database where migrations were just run.

```rust
// In repo_src/frontend/src/server_fns.rs tests:
#[cfg(all(test, feature = "ssr"))]
mod tests {
    use super::*;
    use leptos::create_runtime;
    use crate::database::{self, get_db_pool_test};

    #[tokio::test]
    async fn test_add_get_delete_item_server_fns() {
        // Set env var for init_pool() to pick up sqlite::memory: in test mode
        std::env::set_var("TEST_DATABASE_URL_FOR_SERVER_FN_TESTS", "sqlite::memory:");

        let rt = leptos::create_runtime();

        // Setup: run migrations on the in-memory DB that server functions will use
        let test_db_conn_for_migrations = get_db_pool_test().await.unwrap();
        sqlx::migrate!("./migrations") // Path relative to frontend crate
            .run(&test_db_conn_for_migrations)
            .await
            .expect("Migrations failed for server_fn test setup");

        // 1. Add item
        let item_text = "Test item from server_fn".to_string();
        assert!(add_item(item_text.clone()).await.is_ok());

        // 2. Get items
        let items = get_items().await.expect("get_items failed");
        let added_item = items.iter().find(|item| item.text == item_text).expect("Added item not found");
        let item_id = added_item.id;

        // 3. Delete item
        assert!(delete_item(item_id).await.is_ok());

        // 4. Verify deletion
        let items_after_delete = get_items().await.expect("get_items after delete failed");
        assert!(items_after_delete.iter().find(|item| item.id == item_id).is_none(), "Item not deleted");
        
        rt.dispose();
        std::env::remove_var("TEST_DATABASE_URL_FOR_SERVER_FN_TESTS");
    }
}
```

This setup allows server functions to be tested against a predictable, isolated database environment.
For a more decoupled approach, consider refactoring database functions to accept `&SqlitePool` and using `leptos::provide_context` / `leptos::use_context` to inject the pool into server functions during tests.

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

    test('should load homepage and add an item', async ({ page }) => {
      await page.goto('http://127.0.0.1:3000');
      await expect(page.locator('h1')).toHaveText('Item Management');
      
      await page.fill('input[name="text"]', 'My E2E Test Item');
      await page.click('button[type="submit"]');
      
      // Wait for item to appear (adjust selector and text as needed)
      await expect(page.locator('.item-list .item-text')).toHaveText('My E2E Test Item');
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
cargo test --workspace
```

## Tips for Testable Code

*   **Separate Concerns:** Keep UI logic (in components) separate from business logic (in server functions, helper modules, or `database.rs`).
*   **Pure Functions:** Write pure functions where possible, as they are easiest to test.
*   **Dependency Injection:** For complex scenarios, consider how dependencies (like database connections) are provided to functions, allowing for mocks or test instances to be injected. (Leptos context system or passing `&SqlitePool` directly are good patterns).

## Testing the Current Template

Focus on:
1.  **Compilation Tests:** `cargo check --workspace` and `cargo leptos build`.
2.  **Unit/Integration Tests for Database Logic:** In `repo_src/frontend/src/database.rs`.
3.  **Integration Tests for Server Functions:** In `repo_src/frontend/src/server_fns.rs`.

## Next Steps

As you develop features:
1.  Add unit tests for any new business logic functions.
2.  Add integration tests for new server functions.
3.  Refine database interaction patterns for better testability if needed (e.g., consistently passing `&SqlitePool`).
4.  Consider setting up E2E tests for critical user flows as the application grows. 