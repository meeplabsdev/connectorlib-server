use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    health: i32,
    hunger: i32,
    breath: i32,
    saturation: i32,
    exhaustion: i32,
    exp_level: i32,
    exp_prog: f32,
    protection: i32,
    gamemode: String,
    fps: i32,
    ping: i32,
    effects: Vec<(String, String, i32, i32, i32)>,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated || sess.playerid.is_none() || sess.serverid.is_none() {
        return None;
    }

    let tx = sess.pclient.transaction().await.unwrap();
    let attributesid = tx
        .query(
            "
            WITH spl AS (
                SELECT id FROM server_player
                WHERE server = $1 AND player = $2
            ),
            gmd_ins AS (
                INSERT INTO gamemode (gamemode)
                VALUES ($3)
                ON CONFLICT (gamemode) DO NOTHING
                RETURNING id
            ),
            gmd AS (
                SELECT id FROM gmd_ins
                UNION ALL
                SELECT id FROM gamemode WHERE gamemode = $3 AND NOT EXISTS (SELECT 1 FROM gmd_ins)
            )

            INSERT INTO attributes (server_player, health, hunger, breath, protection, saturation, exhaustion, exp_level, exp_prog, gamemode, ping, fps)
            SELECT spl.id, $4, $5, $6, $7, $8, $9, $10, $11, gmd.id, $12, $13
            FROM spl, gmd
            ON CONFLICT (server_player) DO UPDATE
            SET health = $4, hunger = $5, breath = $6, protection = $7, saturation = $8, exhaustion = $9, exp_level = $10, exp_prog = $11, gamemode = EXCLUDED.gamemode, ping = $12, fps = $13
            RETURNING id;",
            &[&sess.serverid, &sess.playerid, &msg.gamemode, &(msg.health as i16), &(msg.hunger as i16), &(msg.breath as i16), &(msg.protection as i16), &(msg.saturation as i16), &(msg.exhaustion as i16), &msg.exp_level, &msg.exp_prog, &(msg.ping as i16), &(msg.fps as i16)],
        )
        .await;

    if attributesid.is_err() {
        let _ = tx.rollback().await;
        return None;
    }

    let attributesid = attributesid.unwrap()[0].get::<usize, i32>(0);
    for (name, r#type, colour, duration, strength) in msg.effects {
        let effect = tx
            .execute(
                "
                WITH eff_ins AS (
                    INSERT INTO effect (effect, colour, type)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (effect) DO NOTHING
                    RETURNING id
                ),
                eff AS (
                    SELECT id FROM eff_ins
                    UNION ALL
                    SELECT id FROM effect WHERE effect = $1 AND NOT EXISTS (SELECT 1 FROM eff_ins)
                )

                INSERT INTO effect_instance (attributes, effect, duration, strength)
                SELECT $4, eff.id, $5, $6
                FROM eff;",
                &[&name, &colour, &r#type, &attributesid, &duration, &strength],
            )
            .await;

        if effect.is_err() {
            let _ = tx.rollback().await;
            return None;
        }
    }

    let _ = tx.commit().await;
    return None;
}
