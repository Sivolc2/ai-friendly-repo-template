use serde::{Deserialize, Serialize};
use chrono::NaiveDateTime;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Item {
    pub id: i64,
    pub text: String,
    // Store as NaiveDateTime if your DB doesn't handle timezone well, convert to DateTime<Utc> in app logic
    // Or, ensure DB stores with timezone and read as DateTime<Utc>
    // For SQLite, it's often simpler to store as TEXT (ISO8601) or INTEGER (unix timestamp)
    // and parse. SQLx handles NaiveDateTime to TEXT for SQLite by default.
    pub created_at: NaiveDateTime, // Example: 2023-10-26 09:30:00
}

// If you need to pass DateTime<Utc> directly from server fns and deserialize on client:
// #[derive(Clone, Debug, Serialize, Deserialize)]
// pub struct Item {
//     pub id: i64,
//     pub text: String,
//     #[serde(with = "chrono::serde::ts_milliseconds")] // Example for serde with chrono
//     pub created_at: DateTime<Utc>,
// } 