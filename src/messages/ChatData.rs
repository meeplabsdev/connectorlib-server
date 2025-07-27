use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{handlers::SocketResponse, session::Session, utils};

#[derive(Deserialize, Debug)]
pub struct Message {
    message: String,
    mtype: String,
    from: String,
    to: String,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated
        || sess.playerid.is_none()
        || msg.message.is_empty()
        || msg.mtype.is_empty()
    {
        return None;
    }

    let from = match Uuid::parse_str(&msg.from) {
        Ok(uuid) => uuid,
        Err(_) => Uuid::parse_str("00000000-0000-0000-0000-000000000000").unwrap(),
    };

    let to = match Uuid::parse_str(&msg.to) {
        Ok(uuid) => uuid,
        Err(_) => Uuid::parse_str("00000000-0000-0000-0000-000000000000").unwrap(),
    };

    let from = utils::get_username(from, &sess.hclient)
        .await
        .unwrap_or("".to_string());
    let to = utils::get_username(to, &sess.hclient)
        .await
        .unwrap_or("".to_string());

    let _ = sess
        .pclient
        .execute(
            "
                WITH ins AS (
                    INSERT INTO message_type (type)
                    VALUES ($1)
                    ON CONFLICT (type) DO NOTHING
                    RETURNING id
                ),
                sel AS (
                    SELECT id FROM ins
                    UNION ALL
                    SELECT id FROM message_type WHERE type = $1 AND NOT EXISTS (SELECT 1 FROM ins)
                ),
                fro AS (
                    INSERT INTO player (uuid, username, reputation, added, active)
                    VALUES ($2, $3, 0, NOW(), NOW())
                    ON CONFLICT (uuid) DO NOTHING
                    RETURNING id
                ),
                too AS (
                    INSERT INTO player (uuid, username, reputation, added, active)
                    VALUES ($4, $5, 0, NOW(), NOW())
                    ON CONFLICT (uuid) DO NOTHING
                    RETURNING id
                ),
                fro_id AS (
                    SELECT id FROM fro
                    UNION ALL
                    SELECT id FROM player WHERE uuid = $2 AND NOT EXISTS (SELECT 1 FROM fro)
                ),
                too_id AS (
                    SELECT id FROM too
                    UNION ALL
                    SELECT id FROM player WHERE uuid = $4 AND NOT EXISTS (SELECT 1 FROM too)
                )
                INSERT INTO messages (server, type, message, pfrom, pto, sent)
                SELECT $7, sel.id, $6, fro_id.id, too_id.id, NOW()
                FROM sel, fro_id, too_id;",
            &[
                &msg.mtype,
                &msg.from,
                &from,
                &msg.to,
                &to,
                &msg.message,
                &sess.serverid,
            ],
        )
        .await;

    return None;
}
