pub mod app_component;
pub mod components;
pub mod error_template;

#[cfg(feature = "ssr")]
pub mod server_fns;

#[cfg(feature = "ssr")]
pub mod database; // For server-side logic, accessible in server_fns
// pub mod models; // if models are separate from shared, usually on server side

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    use leptos::*;
    use app_component::AppComponent;
    use leptos_meta::provide_meta_context;

    _ = console_log::init_with_level(log::Level::Debug);
    console_error_panic_hook::set_once();

    leptos::mount_to_body(move || {
        provide_meta_context();
        view! { <AppComponent /> }
    });
} 