use uuid::Uuid;
use tokio_postgres::{ tls::NoTlsStream, NoTls, Socket };

use crate::utils;

#[allow(dead_code)]
pub struct Session {
    pub client: tokio_postgres::Client,
    connection: tokio_postgres::Connection<Socket, NoTlsStream>,

    uuid: Option<Uuid>,
    username: Option<String>,

    token: String,
    authenticity: String,
    authenticated: bool,
}

#[allow(dead_code)]
impl Session {
    pub async fn new() -> Self {
        let (client, connection) = tokio_postgres;
        let host = "localhost";
        if utils::is_docker() {
            host = "postgres";
        }

        ::connect(
            "user=connectorlib password=connectorlib dbname=connectorlib host=" + host,
            NoTls
        ).await.unwrap();

        Self {
            client: client,
            connection: connection,

            uuid: None,
            username: None,

            token: "".to_string(),
            authenticity: "".to_string(),
            authenticated: false,
        }
    }

    pub fn set_identity(&mut self, uuid: Uuid, username: String) {
        self.uuid = Some(uuid);
        self.username = Some(username);
    }

    pub fn get_identity(&self) -> Option<(Uuid, String)> {
        if self.uuid.is_none() || self.username.is_none() {
            return None;
        }

        return Some((self.uuid.unwrap(), self.username.clone().unwrap()));
    }

    pub fn set_authenticity(&mut self, authenticity: String) {
        self.authenticity = authenticity;
    }

    pub fn is_authenticity(&self, authenticity: String) -> bool {
        return self.authenticity.eq(&authenticity);
    }

    pub fn authenticate(&mut self, token: String) {
        self.token = token;
        self.authenticated = true;
    }

    pub fn is_authenticated(&self) -> bool {
        return self.authenticated;
    }
}
