use crate::{handlers::SocketResponse, session::Session, utils};
use futures_util::future::join_all;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::task::JoinHandle;
use uuid::Uuid;

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
    nearby: HashMap<String, Vec<f32>>,
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

    let mut valid: Vec<(String, Vec<f32>)> = Vec::new();
    for (uuid, pos) in msg.nearby.iter() {
        let uuid = uuid.replace("-", "");
        if pos.len() != 3 {
            continue;
        }
        valid.push((uuid, pos.clone()));
    }
    let uuids: Vec<String> = valid.iter().map(|(uuid, _)| uuid.clone()).collect();
    let result = sess
        .pclient
        .query(
            "SELECT uuid, username FROM player WHERE uuid = ANY($1)",
            &[&uuids],
        )
        .await
        .unwrap();

    let dbunames: HashMap<String, String> = result
        .into_iter()
        .map(|row| (row.get::<usize, String>(0), row.get::<usize, String>(1)))
        .collect();

    let mut usernames: Vec<JoinHandle<Option<(String, String)>>> = Vec::new();
    for (uuid, _pos) in &valid {
        if !dbunames.contains_key(uuid) {
            let uuid_clone = uuid.clone();
            let hclient = sess.hclient.clone();

            let task = tokio::spawn(async move {
                let parsed_uuid = match Uuid::parse_str(&uuid_clone) {
                    Ok(uuid) => uuid,
                    Err(_) => return None,
                };

                let username = match utils::get_username(parsed_uuid, &hclient).await {
                    Ok(username) => username,
                    Err(_) => return None,
                };

                Some((uuid_clone, username))
            });

            usernames.push(task);
        }
    }

    let _usernames = join_all(usernames).await;
    let mut usernames: HashMap<String, String> = HashMap::new();
    for result in _usernames {
        if let Ok(Some((uuid, username))) = result {
            usernames.insert(uuid, username);
        }
    }

    let mut nearby: HashMap<String, (String, Vec<f32>)> = HashMap::new();
    for (uuid, pos) in valid {
        let username = if let Some(username) = dbunames.get(&uuid) {
            username.clone()
        } else if let Some(username) = usernames.get(&uuid) {
            username.clone()
        } else {
            continue;
        };

        nearby.insert(uuid, (username, pos));
    }

    let tx = sess.pclient.transaction().await.unwrap();
    let positionid = tx.query(
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
            FROM dim, spl
            RETURNING id;",
        &[&msg.dimension, &sess.serverid, &sess.playerid, &msg.position, &msg.velocity, &msg.sneaking, &msg.sprinting, &msg.swimming, &msg.crawling, &msg.grounded, &msg.fallflying],
    ).await;

    if positionid.is_err() {
        let _ = tx.rollback().await;
        return None;
    }

    let positionid = positionid.unwrap()[0].get::<usize, i32>(0);
    for (uuid, (username, pos)) in nearby {
        let near = tx
            .execute(
                "
                    WITH ins_pla AS (
                        INSERT INTO player (uuid, username, reputation, added, active)
                        VALUES ($1, $2, 0, NOW(), NOW())
                        ON CONFLICT (uuid) DO NOTHING
                        RETURNING id
                    ),
                    pla AS (
                        SELECT id FROM player
                        UNION ALL
                        SELECT id FROM player WHERE uuid = $2 AND NOT EXISTS (SELECT 1 FROM player)
                    )
                    INSERT INTO nearby (position, player, location)
                    SELECT $3, pla.id, $4
                    FROM pla;",
                &[&uuid, &username, &positionid, &pos],
            )
            .await;

        if near.is_err() {
            let _ = tx.rollback().await;
            return None;
        }
    }

    let _ = tx.commit().await;
    return None;
}
