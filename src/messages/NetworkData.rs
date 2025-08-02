use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    ip: String,
    user_agent: String,
    via: String,
    forwarded: String,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated {
        return None;
    }

    let _ = sess
        .pclient
        .execute(
            "
                INSERT INTO network_data (player, ip, user_agent, via, forwarded, added, active)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                ON CONFLICT (ip) DO UPDATE
                SET active = NOW();",
            &[
                &sess.playerid,
                &msg.ip,
                &msg.user_agent,
                &msg.via,
                &msg.forwarded,
            ],
        )
        .await;

    return None;
}
