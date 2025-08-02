use serde::{ Deserialize, Serialize };

use crate::messages::*;
use crate::session::Session;

#[allow(dead_code)]
#[derive(Deserialize, Debug)]
#[serde(tag = "id", content = "value")]
pub enum SocketMessage {
    ClientAttributes(ClientAttributes::Message),
    ClientChat(ClientChat::Message),
    ClientPosition(ClientPosition::Message),
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
    ClientAttributes(ClientAttributes::Response),
    ClientChat(ClientChat::Response),
    ClientPosition(ClientPosition::Response),
    IdentityChallenge(IdentityChallenge::Response),
    IdentityRequest(IdentityRequest::Response),
    NetworkData(NetworkData::Response),
    PlayerJoin(PlayerJoin::Response),
    PlayerQuit(PlayerQuit::Response),
}

pub async fn handle(message: SocketMessage, sess: &mut Session) -> Option<SocketResponse> {
    match message {
        SocketMessage::ClientAttributes(msg) => ClientAttributes::handle(msg, sess).await,
        SocketMessage::ClientChat(msg) => ClientChat::handle(msg, sess).await,
        SocketMessage::ClientPosition(msg) => ClientPosition::handle(msg, sess).await,
        SocketMessage::IdentityChallenge(msg) => IdentityChallenge::handle(msg, sess).await,
        SocketMessage::IdentityRequest(msg) => IdentityRequest::handle(msg, sess).await,
        SocketMessage::NetworkData(msg) => NetworkData::handle(msg, sess).await,
        SocketMessage::PlayerJoin(msg) => PlayerJoin::handle(msg, sess).await,
        SocketMessage::PlayerQuit(msg) => PlayerQuit::handle(msg, sess).await,
    }
}
