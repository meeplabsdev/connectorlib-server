use serde::{ Deserialize, Serialize };
use uuid::Uuid;

use crate::{ handlers::SocketMessage, session::Session };

#[derive(Serialize, Deserialize, Debug)]
pub struct Message {
    uuid: String,
    username: String,
}

pub fn handle(msg: Message, _sess: &Session) -> Option<SocketMessage> {
    println!("{} {}", msg.uuid, msg.username);
    let id = Uuid::new_v4().to_string().replace("-", "");
    println!("Generated nonce {}", id);

    // return Some(
    //     SocketMessage::IdentityRequest(Message {
    //         uuid: "test".to_string(),
    //         username: "test2".to_string(),
    //     })
    // );

    return None;
}
