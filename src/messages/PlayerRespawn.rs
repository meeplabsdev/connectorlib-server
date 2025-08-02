use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    position: Vec<f32>,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated || sess.playerid.is_none() || sess.serverid.is_none() {
        return None;
    }

    let _ = sess
        .pclient
        .execute(
            "
            WITH spl AS (
                SELECT id FROM server_player
                WHERE server = $1 AND player = $2
            )

            INSERT INTO deaths (server_player, position, added)
            SELECT spl.id, $3, NOW()
            FROM spl;",
            &[&sess.serverid, &sess.playerid, &msg.position],
        )
        .await;

    return None;
}
