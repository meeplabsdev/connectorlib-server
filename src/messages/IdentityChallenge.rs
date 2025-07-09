use serde::{ Deserialize, Serialize };
use uuid::Uuid;

use crate::{ handlers::SocketResponse, session::Session };

#[derive(Deserialize, Debug)]
pub struct Message {
    authenticity: String,
}

#[derive(Serialize, Debug)]
pub struct Response {
    token: String,
}

pub fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if sess.is_authenticity(msg.authenticity) {
        let token = Uuid::new_v4().to_string().replace("-", "");
        sess.authenticate(token.clone());

        return Some(
            SocketResponse::IdentityChallenge(Response {
                token: token.clone(),
            })
        );
    }

    return None;
}
