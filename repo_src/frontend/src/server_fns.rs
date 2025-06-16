use leptos::*;
// No explicit serde import needed here as #[server] handles it.
// database functions are now in crate::database
// shared::Item is used for return types/params.
#[cfg(feature = "ssr")] // Only compile the database interactions on the server
use crate::database::{add_item_db, delete_item_db, get_all_items_db};
use shared::Item;


// If GetItemsParams was previously defined and used:
// use serde::{Deserialize, Serialize};
// #[derive(Serialize, Deserialize, Clone, Debug)]
// pub struct GetItemsParams {}

// The first argument to `#[server]` is the name of the generated struct for this server function.
// If it takes no arguments (like a simple GET), you can pass () when calling it,
// or define an empty params struct. For simplicity, let's assume no explicit params struct.
#[server(GetItems, "/api")]
pub async fn get_items() -> Result<Vec<Item>, ServerFnError> {
    // This part of the code will only be compiled and run on the server
    #[cfg(feature = "ssr")]
    {
        // log::debug!("Executing get_items_server_fn on server");
        match get_all_items_db().await {
            Ok(items) => Ok(items),
            Err(db_error_string) => {
                leptos::logging::error!("Server function GetItems failed: {}", db_error_string);
                Err(ServerFnError::ServerError(db_error_string))
            }
        }
    }

    // This part is for the client-side stub, it won't be executed for real.
    // However, the function signature must be valid Rust.
    #[cfg(not(feature = "ssr"))]
    {
        // log::debug!("Calling get_items_server_fn (stub) on client");
        // Client-side stub, never called in practice if SSR is working
        // but needs to compile.
        unreachable!("get_items should only run on the server")
    }
}

// AddItem takes `text: String` as a parameter.
// The `#[server]` macro will generate a struct `AddItem { text: String }`.
#[server(AddItem, "/api")]
pub async fn add_item(text: String) -> Result<(), ServerFnError> {
    #[cfg(feature = "ssr")]
    {
        // log::debug!("Executing add_item_server_fn on server with text: {}", text);
        if text.trim().is_empty() {
            return Err(ServerFnError::Args("Item text cannot be empty.".into()));
        }
        if text.len() > 100 {
            return Err(ServerFnError::Args("Item text too long (max 100 chars).".into()));
        }
        match add_item_db(text).await {
            Ok(_) => Ok(()),
            Err(db_error_string) => {
                leptos::logging::error!("Server function AddItem failed: {}", db_error_string);
                Err(ServerFnError::ServerError(db_error_string))
            }
        }
    }
    #[cfg(not(feature = "ssr"))]
    { 
        unreachable!("add_item should only run on the server")
    }
}

// DeleteItem takes `id: i64` as a parameter.
// The `#[server]` macro will generate a struct `DeleteItem { id: i64 }`.
#[server(DeleteItem, "/api")]
pub async fn delete_item(id: i64) -> Result<(), ServerFnError> {
    #[cfg(feature = "ssr")]
    {
        // log::debug!("Executing delete_item_server_fn on server with id: {}", id);
        match delete_item_db(id).await {
            Ok(_) => Ok(()),
            Err(db_error_string) => {
                leptos::logging::error!("Server function DeleteItem failed: {}", db_error_string);
                Err(ServerFnError::ServerError(db_error_string))
            }
        }
    }
    #[cfg(not(feature = "ssr"))]
    { 
        unreachable!("delete_item should only run on the server")
    }
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