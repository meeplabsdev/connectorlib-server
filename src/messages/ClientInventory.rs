use serde::{Deserialize, Serialize};

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    slot_selected: i32,
    items: Vec<(String, String, i32, i32)>,
}

#[derive(Serialize, Debug)]
pub struct Response {}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if !sess.authenticated || sess.playerid.is_none() || sess.serverid.is_none() {
        return None;
    }

    let tx = sess.pclient.transaction().await.unwrap();
    let inventoryid = tx
        .query(
            "
            WITH spl AS (
                SELECT id FROM server_player
                WHERE server = $1 AND player = $2
            )

            INSERT INTO inventory (server_player, slot_selected)
            SELECT spl.id, $3
            FROM spl
            ON CONFLICT (server_player) DO UPDATE
            SET slot_selected = $3
            RETURNING id;",
            &[&sess.serverid, &sess.playerid, &msg.slot_selected],
        )
        .await;

    if inventoryid.is_err() {
        let _ = tx.rollback().await;
        return None;
    }

    let inventoryid = inventoryid.unwrap()[0].get::<usize, i32>(0);
    let del = tx
        .execute(
            "
            DELETE FROM item_instance WHERE inventory = $1;",
            &[&inventoryid],
        )
        .await;

    if del.is_err() {
        let _ = tx.rollback().await;
        return None;
    }

    for (item, custom, slot, count) in msg.items {
        let item_instance = tx
            .execute(
                "
                WITH itm_ins AS (
                    INSERT INTO item (item)
                    VALUES ($1)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                ),
                itm AS (
                    SELECT id FROM itm_ins
                    UNION ALL
                    SELECT id FROM item WHERE item = $1 AND NOT EXISTS (SELECT 1 FROM itm_ins)
                )

                INSERT INTO item_instance (inventory, item, slot, count, custom)
                SELECT $2, itm.id, $3, $4, $5
                FROM itm;",
                &[&item, &inventoryid, &slot, &count, &custom],
            )
            .await;

        if item_instance.is_err() {
            let _ = tx.rollback().await;
            return None;
        }
    }

    let _ = tx.commit().await;
    return None;
}
