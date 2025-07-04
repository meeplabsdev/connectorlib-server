use serde::{ Deserialize, Serialize };

use crate::messages::*;
use crate::session::Session;

#[derive(Deserialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketMessage {
    IdentityRequest(IdentityRequest::Message),
}

#[derive(Serialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketResponse {
    IdentityRequest(IdentityRequest::Response),
}

pub fn handle(message: SocketMessage, sess: &Session) -> Option<SocketResponse> {
    match message {
        SocketMessage::IdentityRequest(msg) => IdentityRequest::handle(msg, sess),
    }
}
