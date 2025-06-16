use leptos::*;
use shared::Item;
use crate::server_fns::DeleteItem; // Use the server function struct

#[component]
pub fn ItemList(
    items: Vec<Item>,
    delete_item_action: Action<DeleteItem, Result<(), ServerFnError>>,
) -> impl IntoView {
    if items.is_empty() {
        return view! { <p>"No items to display."</p> }.into_view();
    }

    view! {
        <ul class="item-list">
            <For
                each=move || items.clone()
                key=|item| item.id
                children=move |item| {
                    let item_for_delete = item.clone(); // Clone for the closure
                    let on_delete_click = move |_| {
                        // Dispatch the action with parameters matching the fields of DeleteItem
                        delete_item_action.dispatch(DeleteItem { id: item_for_delete.id });
                    };

                    // Check if this specific item's deletion is pending
                    let is_deleting_this_item = Signal::derive(move || {
                        delete_item_action.pending().get() &&
                        delete_item_action.input().get().map_or(false, |params| params.id == item.id)
                    });

                    view! {
                        <li class="item">
                            <span class="item-text">{item.text.clone()}</span>
                            <span class="item-date">{item.created_at.format("%Y-%m-%d %H:%M:%S").to_string()}</span>
                            <button
                                class="item-delete"
                                on:click=on_delete_click
                                disabled=is_deleting_this_item
                            >
                                {move || if is_deleting_this_item.get() { "Deleting..." } else { "Delete" }}
                            </button>
                        </li>
                    }
                }
            />
        </ul>
        {move || { // Global error for delete action, if any
            delete_item_action.value().get().map(|result| match result {
                Err(e) => view! { <p class="error-detail" style="color: red;">{format!("Error deleting item: {}", e)}</p> }.into_view(),
                Ok(_) => view! { <></> }.into_view(),
            })
        }}
    }.into_view()
} 