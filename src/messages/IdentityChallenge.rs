use libaes::Cipher;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    authenticity: String,
}

#[derive(Serialize, Debug)]
pub struct Response {
    token: String,
}

pub fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if sess.authenticity.eq(&msg.authenticity) {
        let token = Uuid::new_v4()
            .to_string()
            .replace("-", "")
            .chars()
            .take(16)
            .collect::<String>();
        assert!(token.len() == 16);

        let btoken: [u8; 16] = token
            .clone()
            .as_bytes()
            .try_into()
            .expect("Invalid token length");

        sess.token = token.clone();
        sess.btoken = Cipher::new_128(&btoken);
        sess.authenticated = true;

        return Some(SocketResponse::IdentityChallenge(Response {
            token: token.clone(),
        }));
    }

    return None;
}
