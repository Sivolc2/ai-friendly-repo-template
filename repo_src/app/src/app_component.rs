use leptos::*;
use leptos_meta::*;

#[component]
pub fn AppComponent() -> impl IntoView {
    provide_meta_context();

    view! {
        <Title text="Simple Item List"/>
        <main class="container">
            <h1>"Item Management"</h1>
            <p>"Hello, World! The app is working."</p>
        </main>
    }
} 