use leptos::*;
use serde::{Deserialize, Serialize}; // Add explicit serde import
use crate::database::{add_item_db, delete_item_db, get_all_items_db};
use shared::Item; // Assuming Item is in shared crate

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct GetItemsParams {}

#[server(GetItems, "/api")]
pub async fn get_items_server_fn(_params: GetItemsParams) -> Result<Vec<Item>, ServerFnError<String>> {
    // In a real app, you might pass a DB connection pool via context
    // For simplicity here, database.rs functions might use a static pool
    get_all_items_db().await
}


#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AddItemParams {
    pub text: String,
}
#[server(AddItem, "/api")]
pub async fn add_item_server_fn(params: AddItemParams) -> Result<(), ServerFnError<String>> {
    if params.text.trim().is_empty() {
        return Err(ServerFnError::Args("Item text cannot be empty".into()));
    }
    if params.text.len() > 100 {
         return Err(ServerFnError::Args("Item text too long (max 100 chars)".into()));
    }
    add_item_db(params.text).await
}


#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct DeleteItemParams {
    pub id: i64,
}
#[server(DeleteItem, "/api")]
pub async fn delete_item_server_fn(params: DeleteItemParams) -> Result<(), ServerFnError<String>> {
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