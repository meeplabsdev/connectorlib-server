use std::path::Path;

use uuid::Uuid;

pub fn is_docker() -> bool {
    Path::new("/.dockerenv").exists()
}

pub async fn get_username(uuid: Uuid, hclient: &reqwest::Client) -> Result<String, String> {
    let response = hclient
        .get(format!(
            "https://playerdb.co/api/player/minecraft/{}",
            uuid.to_string()
        ))
        .send()
        .await;

    if response.is_err() {
        return Err("Failed to send request".to_string());
    }

    let response = response.unwrap().json::<serde_json::Value>().await.unwrap();
    let username = response["data"]["player"]["username"].as_str();

    if username.is_none() || username.unwrap().is_empty() {
        return Err("Failed to get username".to_string());
    }

    Ok(username.unwrap().to_string())
}
