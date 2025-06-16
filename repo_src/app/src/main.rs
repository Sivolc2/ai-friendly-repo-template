#[cfg(feature = "ssr")]
#[tokio::main]
async fn main() {
    use axum::Router;
    use leptos::*;
    use leptos_axum::{generate_route_list, LeptosRoutes};
    use app::app_component::AppComponent; // Use the renamed component
    use tower_http::services::ServeDir;
    
    #[cfg(feature = "DATABASE_AUTO_MIGRATE")]
    use app::database; // For migrations

    // Load .env file if present
    match dotenvy::dotenv() {
        Ok(path) => leptos::logging::log!("Loaded .env file from: {:?}", path),
        Err(_) => leptos::logging::log!("No .env file found, using environment variables directly or defaults."),
    }

    // Run migrations if the feature is enabled
    #[cfg(feature = "DATABASE_AUTO_MIGRATE")]
    {
        if let Err(e) = database::run_migrations().await {
            leptos::logging::error!("Failed to run database migrations: {:?}", e);
            // Depending on your error handling strategy, you might want to exit here
            // std::process::exit(1);
        }
    }


    let conf = get_configuration(None).await.unwrap();
    let leptos_options = conf.leptos_options;
    let addr = leptos_options.site_addr;
    let routes = generate_route_list(AppComponent);

    // build our application with a route
    let app = Router::new()
        .leptos_routes(&leptos_options, routes, AppComponent)
        .fallback_service(ServeDir::new(leptos_options.site_root.clone()))
        .with_state(leptos_options);

    leptos::logging::log!("listening on http://{}", &addr);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app.into_make_service()).await.unwrap();
}

#[cfg(not(feature = "ssr"))]
pub fn main() {
    // no client-side main function
    // all logic is handled by the lib.rs hydrate function called by wasm-bindgen
} 