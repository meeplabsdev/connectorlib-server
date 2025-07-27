use serde::{ Deserialize, Serialize };

use crate::messages::*;
use crate::session::Session;

#[allow(dead_code)]
#[derive(Deserialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketMessage {
    ChatData(ChatData::Message),
    IdentityChallenge(IdentityChallenge::Message),
    IdentityRequest(IdentityRequest::Message),
    NetworkData(NetworkData::Message),
    PlayerJoin(PlayerJoin::Message),
    PlayerQuit(PlayerQuit::Message),
}

#[allow(dead_code)]
#[derive(Serialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketResponse {
    ChatData(ChatData::Response),
    IdentityChallenge(IdentityChallenge::Response),
    IdentityRequest(IdentityRequest::Response),
    NetworkData(NetworkData::Response),
    PlayerJoin(PlayerJoin::Response),
    PlayerQuit(PlayerQuit::Response),
}

pub async fn handle(message: SocketMessage, sess: &mut Session) -> Option<SocketResponse> {
    match message {
        SocketMessage::ChatData(msg) => ChatData::handle(msg, sess).await,
        SocketMessage::IdentityChallenge(msg) => IdentityChallenge::handle(msg, sess).await,
        SocketMessage::IdentityRequest(msg) => IdentityRequest::handle(msg, sess).await,
        SocketMessage::NetworkData(msg) => NetworkData::handle(msg, sess).await,
        SocketMessage::PlayerJoin(msg) => PlayerJoin::handle(msg, sess).await,
        SocketMessage::PlayerQuit(msg) => PlayerQuit::handle(msg, sess).await,
    }
}
