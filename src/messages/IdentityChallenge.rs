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
    if !sess.authenticity.eq(&msg.authenticity) || sess.username.is_none() || sess.uuid.is_none() {
        return None;
    }

    if !DEV {
        let response = sess.hclient.get(format!("https://sessionserver.mojang.com/session/minecraft/hasJoined?username={}&serverId={}", sess.username.clone().unwrap(), msg.serverid)).send().await.unwrap();
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
                    INSERT INTO player (uuid, username, reputation, added, active)
                    VALUES ($1, $2, 0, NOW(), NOW())
                    ON CONFLICT (uuid) DO UPDATE
                    SET active = NOW()
                    RETURNING *
                )
                SELECT id FROM ins
                UNION ALL
                SELECT id FROM player WHERE uuid = $1 AND NOT EXISTS (SELECT 1 FROM ins);",
            &[
                &sess.uuid.unwrap().to_string().replace("-", ""),
                &sess.username.clone().unwrap(),
            ],
        )
        .await
        .unwrap();

    sess.playerid = Some(player[0].get::<usize, i32>(0));

    return Some(SocketResponse::IdentityChallenge(Response {
        token: token.clone(),
    }));
}
