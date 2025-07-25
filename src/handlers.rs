use serde::{ Deserialize, Serialize };

use crate::messages::*;
use crate::session::Session;

#[derive(Deserialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketMessage {
    IdentityChallenge(IdentityChallenge::Message),
    IdentityRequest(IdentityRequest::Message),
}

#[derive(Serialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketResponse {
    IdentityChallenge(IdentityChallenge::Response),
    IdentityRequest(IdentityRequest::Response),
}

pub async fn handle(message: SocketMessage, sess: &mut Session) -> Option<SocketResponse> {
    match message {
        SocketMessage::IdentityChallenge(msg) => IdentityChallenge::handle(msg, sess).await,
        SocketMessage::IdentityRequest(msg) => IdentityRequest::handle(msg, sess).await,
    }
}
