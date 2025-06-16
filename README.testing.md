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

    #[tokio::test]
    async fn test_basic_functionality() {
        let _rt = create_runtime(); // Leptos runtime for server functions
        
        // Test server function logic here
        // Note: You may need to mock database dependencies
        
        _rt.dispose();
    }
}
```

**Note on testing server functions that access a database:**
The `database::get_db_pool()` function in this template initializes a global static pool. For testing, you'd typically want a separate test database.
The `get_db_pool_test()` function is provided for this purpose. Tests should ensure this test pool is used.

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

    test('should load homepage', async ({ page }) => {
      await page.goto('http://127.0.0.1:3000');
      await expect(page.locator('h1')).toHaveText('Item Management');
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
*   **Dependency Injection:** For complex scenarios, consider how dependencies (like database connections) are provided to functions, allowing for mocks or test instances to be injected. (Leptos context system can be useful here).

## Testing the Current Template

Since this is a basic template, the main testing focus is on:

1. **Compilation Tests:** `cargo check --workspace` and `cargo leptos build` should complete successfully.
2. **Unit Tests:** Any pure business logic functions you add.
3. **Integration Tests:** Testing server functions once database functionality is fully implemented.

## Next Steps

As you develop features beyond the basic template:

1. Add unit tests for business logic functions.
2. Add integration tests for server functions.
3. Consider setting up E2E tests for critical user flows.
4. Use the `get_db_pool_test()` function for database testing scenarios. 