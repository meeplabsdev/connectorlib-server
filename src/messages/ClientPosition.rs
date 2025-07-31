use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    position: Vec<f32>,
    velocity: Vec<f32>,
    dimension: String,
    sneaking: bool,
    sprinting: bool,
    swimming: bool,
    crawling: bool,
    grounded: bool,
    fallflying: bool,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated
        || sess.playerid.is_none()
        || sess.serverid.is_none()
        || msg.position.len() != 3
        || msg.velocity.len() != 3
        || msg.dimension.is_empty()
    {
        return None;
    }

    let _ = sess
        .pclient
        .execute(
            "
                WITH ins_dim AS (
                    INSERT INTO dimension (dimension)
                    VALUES ($1)
                    ON CONFLICT (dimension) DO NOTHING
                    RETURNING id
                ),
                dim AS (
                    SELECT id FROM ins_dim
                    UNION ALL
                    SELECT id FROM dimension WHERE dimension = $1 AND NOT EXISTS (SELECT 1 FROM ins_dim)
                ),
                spl AS (
                    SELECT id FROM server_player
                    WHERE server = $2 AND player = $3
                )

                INSERT INTO position (server_player, position, velocity, dimension, sneaking, sprinting, swimming, crawling, grounded, fallflying, added)
                SELECT spl.id, $4, $5, dim.id, $6, $7, $8, $9, $10, $11, NOW()
                FROM dim, spl;",
            &[&msg.dimension, &sess.serverid, &sess.playerid, &msg.position, &msg.velocity, &msg.sneaking, &msg.sprinting, &msg.swimming, &msg.crawling, &msg.grounded, &msg.fallflying],
        )
        .await
        .unwrap();

    return None;
}
