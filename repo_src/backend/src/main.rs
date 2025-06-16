// This main.rs is only compiled and run for the server-side binary.
// It relies on the "ssr" feature being active for the `frontend` crate.

#[tokio::main]
async fn main() {
    use axum::Router;
    use leptos::*;
    use leptos_axum::{generate_route_list, LeptosRoutes};
    use frontend::app_component::AppComponent; // AppComponent from the frontend crate
    use tower_http::services::ServeDir;
    use tokio::task::LocalSet;

    // Check for command line arguments
    let args: Vec<String> = std::env::args().collect();
    if args.len() > 1 {
        match args[1].as_str() {
            "--seed" => {
                println!("🌱 Manual database seeding requested...");
                
                // Load .env file before database operations
                match dotenvy::dotenv() {
                    Ok(path) => println!("📄 Loaded .env file from: {:?}", path),
                    Err(_) => println!("⚠️  No .env file found. Using environment variables directly."),
                }
                
                // Run seeding in a LocalSet
                let local = LocalSet::new();
                local.run_until(async move {
                    match frontend::database::seed_database().await {
                        Ok(_) => println!("✅ Manual database seeding completed successfully!"),
                        Err(e) => {
                            println!("❌ Manual database seeding failed: {}", e);
                            std::process::exit(1);
                        }
                    }
                }).await;
                return;
            }
            "--force-seed" => {
                println!("🌱 Force database seeding requested (will add items regardless of existing data)...");
                
                // Load .env file before database operations
                match dotenvy::dotenv() {
                    Ok(path) => println!("📄 Loaded .env file from: {:?}", path),
                    Err(_) => println!("⚠️  No .env file found. Using environment variables directly."),
                }
                
                // Run force seeding in a LocalSet
                let local = LocalSet::new();
                local.run_until(async move {
                    match frontend::database::force_seed_database().await {
                        Ok(_) => println!("✅ Force database seeding completed successfully!"),
                        Err(e) => {
                            println!("❌ Force database seeding failed: {}", e);
                            std::process::exit(1);
                        }
                    }
                }).await;
                return;
            }
            "--help" | "-h" => {
                println!("Leptos Full-Stack Web Application");
                println!("\nUsage:");
                println!("  ./backend              Start the web server");
                println!("  ./backend --seed       Seed the database with initial data (only if empty)");
                println!("  ./backend --force-seed Force seed the database (adds data regardless)");
                println!("  ./backend --help       Show this help message");
                return;
            }
            _ => {
                println!("❌ Unknown argument: {}", args[1]);
                println!("Use --help for available options.");
                std::process::exit(1);
            }
        }
    }

    // Load .env file from the workspace root (repo_src/.env)
    // This needs to happen before any database connection attempts if DB_URL is in .env
    match dotenvy::dotenv() {
        Ok(path) => logging::log!("Loaded .env file from: {:?}", path),
        Err(_) => logging::log!("No .env file found or error loading it. Using environment variables directly or defaults."),
    }
    
    // Setup logging (optional, but good for seeing leptos logs)
    // You can use a more sophisticated logger like `tracing` or `env_logger`.
    // simple_logger::init_with_level(log::Level::Debug).expect("couldn't initialize logger");

    // Wrap the server setup in a LocalSet for Leptos SSR support
    let local = LocalSet::new();
    
    local.run_until(async move {
        // Run migrations if the DATABASE_AUTO_MIGRATE feature is enabled for the backend crate.
        // This feature, in turn, enables frontend/DATABASE_AUTO_MIGRATE.
        #[cfg(feature = "DATABASE_AUTO_MIGRATE")] // This block handles migrations and seeding
        {
            logging::log!("DATABASE_AUTO_MIGRATE feature is enabled for backend. Attempting to run migrations...");
            // Ensure the target directory exists for SQLite file creation if using a file-based DB.
            if let Ok(db_url) = std::env::var("DATABASE_URL") {
                if db_url.starts_with("sqlite:") {
                    let path_str = db_url.trim_start_matches("sqlite:");
                    if let Some(parent_dir) = std::path::Path::new(path_str.split('?').next().unwrap_or("")).parent() {
                        if !parent_dir.exists() {
                            logging::log!("Attempting to create database directory: {:?}", parent_dir);
                            if let Err(e) = std::fs::create_dir_all(parent_dir) {
                                logging::error!("Failed to create database directory {:?}: {:?}", parent_dir, e);
                                // std::process::exit(1); // Exit if directory creation fails, as migrations will likely fail.
                            }
                        }
                    }
                }
            }

            // The database module and run_migrations function are part of the `frontend` crate,
            // compiled under its "ssr" and "DATABASE_AUTO_MIGRATE" features.
            match frontend::database::run_migrations().await {
                Ok(_) => logging::log!("Database migrations completed successfully."),
                Err(e) => {
                    logging::error!("FATAL: Failed to run database migrations: {:?}", e);
                    // Exit if migrations fail, as the app is likely unusable.
                    std::process::exit(1);
                }
            }

            // Conditionally seed the database in development environments
            let leptos_env = std::env::var("LEPTOS_ENV").unwrap_or_else(|_| "PROD".to_string());
            if leptos_env == "DEV" {
                logging::log!("🌱 Development environment detected (LEPTOS_ENV=DEV). Attempting to seed database...");
                if let Err(e) = frontend::database::seed_database().await {
                    logging::error!("Failed to seed database: {:?}", e);
                    // Decide if this is a fatal error. For seeding, perhaps not.
                } else {
                    logging::log!("🌱 Automatic database seeding check completed.");
                }
            } else {
                logging::log!("Production-like environment (LEPTOS_ENV is not DEV). Skipping database seeding.");
            }
        }

        // Leptos configuration is read from Cargo.toml workspace metadata in the workspace root.
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
    }).await;
} 