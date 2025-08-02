use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    dimension: String,
    biome: String,
    cx: i32,
    cz: i32,
    ch: Vec<i32>,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated || sess.serverid.is_none() {
        return None;
    }

    let _ = sess
        .pclient
        .execute(
            "
            WITH dim_ins AS (
                INSERT INTO dimension (dimension)
                VALUES ($1)
                ON CONFLICT (dimension) DO NOTHING
                RETURNING id
            ),
            dim AS (
                SELECT id FROM dim_ins
                UNION ALL
                SELECT id FROM dimension WHERE dimension = $1 AND NOT EXISTS (SELECT 1 FROM dim_ins)
            ),
            bio_ins AS (
                INSERT INTO biome (biome)
                VALUES ($2)
                ON CONFLICT (biome) DO NOTHING
                RETURNING id
            ),
            bio AS (
                SELECT id FROM bio_ins
                UNION ALL
                SELECT id FROM biome WHERE biome = $2 AND NOT EXISTS (SELECT 1 FROM bio_ins)
            )

            INSERT INTO chunk (server, dimension, biome, cx, cz, ch)
            SELECT $3, dim.id, bio.id, $4, $5, $6
            FROM dim, bio
            ON CONFLICT (cx, cz) DO NOTHING;",
            &[
                &msg.dimension,
                &msg.biome,
                &sess.serverid,
                &msg.cx,
                &msg.cz,
                &msg.ch,
            ],
        )
        .await;

    return None;
}
