use leptos::*;
use leptos_meta::Title;

#[cfg(feature = "ssr")]
use http::status::StatusCode;

#[component]
pub fn ErrorTemplate(
    #[prop(optional)] outside_errors: Option<Errors>,
    #[prop(optional)] errors: Option<RwSignal<Errors>>,
) -> impl IntoView {
    let errors = match outside_errors {
        Some(e) => create_rw_signal(e),
        None => match errors {
            Some(e) => e,
            None => panic!("No Errors found and ErrorTemplate expects errors!"),
        },
    };

    #[cfg(feature = "ssr")]
    {
        // ResponseOptions is not available in the frontend crate
        // This would need to be handled in the backend if needed
        let _status_code = StatusCode::INTERNAL_SERVER_ERROR;
    }

    view! {
        <Title text="Error Page"/>
        <main class="container error-page">
            <h1>"Error"</h1>
            <p>"Something went wrong"</p>
            <h2>"Errors:"</h2>
            <For
                // Fix the each prop by wrapping in a closure
                each=move || errors.get()
                // a unique key for each item
                key=|(key, _)| key.clone()
                // renders each item to a view
                children=move | (_, error)| {
                    let error_string = error.to_string();
                    view! {
                        <div class="error-detail">
                             <h3>"Error"</h3>
                             <p>{error_string}</p>
                        </div>
                    }
                }
            />
            <a href="/">"Go to Homepage"</a>
        </main>
    }
} 