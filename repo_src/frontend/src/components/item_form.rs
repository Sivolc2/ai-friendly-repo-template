use leptos::*;
use crate::server_fns::AddItem; // Use the server function struct

#[component]
pub fn ItemForm(add_item_action: Action<AddItem, Result<(), ServerFnError>>) -> impl IntoView {
    let (text, set_text) = create_signal(String::new());

    let on_submit = move |ev: ev::SubmitEvent| {
        ev.prevent_default();
        let current_text = text.get().trim().to_string();
        if current_text.is_empty() {
            // Optionally, show a client-side validation message
            // log::warn!("Item text cannot be empty");
            return;
        }
        // Dispatch the action with parameters matching the fields of the AddItem struct
        // (which correspond to the parameters of the add_item_server_fn)
        add_item_action.dispatch(AddItem { text: current_text });
        set_text.set(String::new()); // Clear input after dispatch
    };

    view! {
        <form class="item-form" on:submit=on_submit>
            <div>
                <label for="item-text">"Item Text:"</label>
                <input
                    type="text"
                    id="item-text"
                    name="text"
                    prop:value=text // Use prop:value for controlled component
                    on:input=move |ev| set_text.set(event_target_value(&ev))
                    required
                    maxlength="100" // Corresponds to server-side validation
                />
            </div>
            <button
                type="submit"
                class="button-primary"
                disabled=move || add_item_action.pending().get() || text.get().trim().is_empty()
            >
                {move || if add_item_action.pending().get() { "Adding..." } else { "Add Item" }}
            </button>
            {move || {
                add_item_action.value().get().map(|result| match result {
                    Err(e) => view! { <p class="error-detail" style="color: red;">{format!("Error: {}", e)}</p>}.into_view(),
                    Ok(_) => view! { <></> }.into_view(), // No message on success, list will update
                })
            }}
        </form>
    }
} 