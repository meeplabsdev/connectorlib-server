use libaes::Cipher;
use tokio_postgres::NoTls;
use uuid::Uuid;

use crate::utils;

#[allow(dead_code)]
pub struct Session {
    pub pclient: tokio_postgres::Client,
    pub hclient: reqwest::Client,

    uuid: Option<Uuid>,
    username: Option<String>,
    pub id: Option<i32>,

    pub token: String,
    pub btoken: Cipher,
    pub authenticity: String,
    pub authenticated: bool,
}

#[allow(dead_code)]
impl Session {
    pub async fn new() -> Self {
        let mut host = "localhost";
        if utils::is_docker() {
            host = "postgres";
        }

        let (client, connection) = tokio_postgres::connect(
            &format!(
                "user=connectorlib password=connectorlib dbname=connectorlib host={}",
                host
            ),
            NoTls,
        )
        .await
        .unwrap();

        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("connection error: {}", e);
            }
        });

        Self {
            pclient: client,
            hclient: reqwest::Client::new(),

            uuid: None,
            username: None,
            id: None,

            token: "".to_string(),
            btoken: Cipher::new_128(&[0; 16]),
            authenticity: "".to_string(),
            authenticated: false,
        }
    }

    pub async fn set_identity(&mut self, uuid: Uuid) -> Result<(), String> {
        self.uuid = Some(uuid);
        self.username = Some(username);
    }

    pub fn get_identity(&self) -> Option<(Uuid, String)> {
        if self.uuid.is_none() || self.username.is_none() {
            return None;
        }

        return Some((self.uuid.unwrap(), self.username.clone().unwrap()));
    }
}
