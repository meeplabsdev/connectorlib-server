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
                    WITH ins AS (
                        INSERT INTO server (name, ip, added, active)
                        VALUES ($1, $1, NOW(), NOW())
                        ON CONFLICT (ip) DO UPDATE
                        SET active = NOW()
                        RETURNING *
                    ),
                    sel AS (
                        SELECT id FROM ins
                        UNION ALL
                        SELECT id FROM server WHERE ip = $1 AND NOT EXISTS (SELECT 1 FROM ins)
                    )

                    INSERT INTO server_player (player, server, added, active)
                    SELECT $2, id, NOW(), NOW() FROM sel
                    ON CONFLICT (player, server) DO UPDATE
                    SET active = NOW()",
            &[&msg.ip, &sess.playerid.unwrap()],
        )
        .await;

    return None;
}
