use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    ip: String,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated || sess.playerid.is_none() {
        return None;
    }

    let _ = sess
        .pclient
        .execute(
            "
                UPDATE server_player sp
                SET active = NOW()
                FROM server s
                WHERE sp.server = s.id
                AND s.ip = $1
                AND sp.player = $2",
            &[&msg.ip, &sess.playerid],
        )
        .await
        .unwrap();

    let _ = sess
        .pclient
        .execute(
            "
                UPDATE server s
                SET active = NOW()
                WHERE s.ip = $1",
            &[&msg.ip],
        )
        .await
        .unwrap();

    return None;
}
