use libaes::Cipher;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    authenticity: String,
}

#[derive(Serialize, Debug)]
pub struct Response {
    token: String,
}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if sess.authenticity.eq(&msg.authenticity) {
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
