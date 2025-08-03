use libaes::Cipher;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{handlers::SocketResponse, session::Session};

#[derive(Deserialize, Debug)]
pub struct Message {
    uuid: String,
}

#[derive(Serialize, Debug)]
pub struct Response {
    nonce: String,
    iv: String,
}

pub async fn handle(msg: Message, sess: &mut Session) -> Option<SocketResponse> {
    if msg.uuid.len() != 32 {
        return None;
    }

    if sess
        .set_identity(Uuid::parse_str(&msg.uuid).unwrap())
        .await
        .is_ok()
    {
        let _det = Uuid::new_v4().to_string().replace("-", "");
        let _det = _det.chars();

        let nonce = _det.clone().skip(16).take(16).collect::<String>();
        let iv = _det.clone().take(16).collect::<String>();

        let plaintext = format!("{}{}", nonce, msg.uuid);
        let plaintext = plaintext.as_bytes();

        let key = std::env::var("CL_KEY").expect("CL_KEY not found in environment.");
        let key: &[u8; 16] = key.as_bytes().try_into().unwrap();
        let cipher = Cipher::new_128(key);

        let expected = cipher.cbc_encrypt(iv.as_bytes(), plaintext);
        sess.authenticity = base16ct::lower::encode_string(&expected);

        return Some(SocketResponse::IdentityRequest(Response {
            nonce: nonce,
            iv: iv,
        }));
    }

    return None;
}
