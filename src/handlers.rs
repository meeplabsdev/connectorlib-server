use serde::{ Deserialize, Serialize };

use crate::messages::*;
use crate::session::Session;

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketMessage {
    IdentityRequest(IdentityRequest::Message),
}

pub fn handle(message: SocketMessage, sess: &Session) {
    match message {
        SocketMessage::IdentityRequest(msg) => IdentityRequest::handle(msg, sess),
    }
}
