// This main.rs is only compiled and run for the server-side binary.
// It relies on the "ssr" feature being active for the `frontend` crate.

#[tokio::main]
async fn main() {
    use axum::Router;
    use leptos::*;
    use leptos_axum::{generate_route_list, LeptosRoutes};
    use frontend::app_component::AppComponent; // AppComponent from the frontend crate
    use tower_http::services::ServeDir;

    // Load .env file from the workspace root (repo_src/.env)
    // This needs to happen before any database connection attempts if DB_URL is in .env
    match dotenvy::dotenv() {
        Ok(path) => logging::log!("Loaded .env file from: {:?}", path),
        Err(_) => logging::log!("No .env file found or error loading it. Using environment variables directly or defaults."),
    }
    
    // Setup logging (optional, but good for seeing leptos logs)
    // You can use a more sophisticated logger like `tracing` or `env_logger`.
    // simple_logger::init_with_level(log::Level::Debug).expect("couldn't initialize logger");


    // Run migrations if the DATABASE_AUTO_MIGRATE feature is enabled for the backend crate.
    // This feature, in turn, enables frontend/DATABASE_AUTO_MIGRATE.
    #[cfg(feature = "DATABASE_AUTO_MIGRATE")]
    {
        logging::log!("DATABASE_AUTO_MIGRATE feature is enabled for backend.");
        // The database module and run_migrations function are part of the `frontend` crate,
        // compiled under its "ssr" and "DATABASE_AUTO_MIGRATE" features.
        match frontend::database::run_migrations().await {
            Ok(_) => logging::log!("Database migrations completed successfully."),
            Err(e) => {
                logging::error!("Failed to run database migrations: {:?}", e);
                // Depending on your error handling strategy, you might want to exit here.
                // std::process::exit(1);
            }
        }
    }


    // Leptos configuration is read from Leptos.toml in the workspace root.
    let conf = get_configuration(None).await.unwrap();
    let leptos_options = conf.leptos_options;
    let addr = leptos_options.site_addr;
    
    // generate_route_list uses the AppComponent from the frontend crate.
    // Server functions defined in `frontend` are automatically registered.
    let routes = generate_route_list(AppComponent);

    let app = Router::new()
        .leptos_routes(&leptos_options, routes, AppComponent)
        .fallback_service(ServeDir::new(leptos_options.site_root.clone()))
        .with_state(leptos_options);

    logging::log!("listening on http://{}", &addr);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app.into_make_service()).await.unwrap();
} 