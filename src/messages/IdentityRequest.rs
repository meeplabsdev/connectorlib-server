use serde::{ Deserialize, Serialize };
use uuid::Uuid;

use crate::session::Session;

#[derive(Serialize, Deserialize, Debug)]
pub struct Message {
    uuid: String,
    username: String,
}

pub fn handle(msg: Message, sess: &Session) {
    println!("{} {}", msg.uuid, msg.username);
    let id = Uuid::new_v4().to_string().replace("-", "");
    println!("Generated nonce {}", id);
}
