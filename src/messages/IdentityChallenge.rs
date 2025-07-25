use libaes::Cipher;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{DEV, handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    authenticity: String,
    serverid: String,
}

#[derive(Serialize, Debug)]
pub struct Response {
    token: String,
}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    let identity = sess.get_identity().unwrap();
    if !sess.authenticity.eq(&msg.authenticity) {
        return None;
    }

    if !DEV {
        let response = sess.hclient.get(format!("https://sessionserver.mojang.com/session/minecraft/hasJoined?username={}&serverId={}", identity.1.clone(), msg.serverid)).send().await.unwrap();
        let response = response.json::<serde_json::Value>().await;

        if response.is_err() || !response.unwrap().as_object().unwrap().contains_key("id") {
            // failed to auth with mojang
            return None;
        }
    }

    let token = Uuid::new_v4()
        .to_string()
        .replace("-", "")
        .chars()
        .take(16)
        .collect::<String>();
    assert!(token.len() == 16);

    let btoken: [u8; 16] = token
        .clone()
        .as_bytes()
        .try_into()
        .expect("Invalid token length");

    sess.token = token.clone();
    sess.btoken = Cipher::new_128(&btoken);
    sess.authenticated = true;

    let player = sess
        .pclient
        .query(
            "
                WITH ins AS (
                    INSERT INTO player (uuid, username, added, active)
                    VALUES ($1, $2, NOW(), NOW())
                    ON CONFLICT (uuid) DO NOTHING
                    RETURNING *
                )
                SELECT id FROM ins
                UNION ALL
                SELECT id FROM player WHERE uuid = $1 AND NOT EXISTS (SELECT 1 FROM ins)",
            &[&identity.0.to_string().replace("-", ""), &identity.1],
        )
        .await
        .unwrap();

    sess.id = Some(player[0].get::<usize, i32>(0));

    return Some(SocketResponse::IdentityChallenge(Response {
        token: token.clone(),
    }));
}
