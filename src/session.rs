use governor::clock::{QuantaClock, QuantaInstant};
use governor::middleware::NoOpMiddleware;
use governor::state::{InMemoryState, NotKeyed};
use governor::{Quota, RateLimiter};
use libaes::Cipher;
use std::num::NonZeroU32;
use std::sync::Arc;
use tokio_postgres::NoTls;
use uuid::Uuid;

use crate::utils;

#[allow(dead_code)]
pub struct Session {
    handle: tokio::task::JoinHandle<()>,
    pub limiter:
        Arc<RateLimiter<NotKeyed, InMemoryState, QuantaClock, NoOpMiddleware<QuantaInstant>>>,
    pub pclient: tokio_postgres::Client,
    pub hclient: reqwest::Client,

    pub uuid: Option<Uuid>,
    pub username: Option<String>,
    pub playerid: Option<i32>,
    pub serverid: Option<i32>,

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
            host = "pgbouncer";
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

        let handle = tokio::spawn(async move {
            if let Err(e) = &connection.await {
                eprintln!("connection error: {}", e);
            }
        });

        let limiter = Arc::new(RateLimiter::direct(Quota::per_second(
            NonZeroU32::new(40).unwrap(),
        )));

        Self {
            handle,
            limiter,
            pclient: client,
            hclient: reqwest::Client::new(),

            uuid: None,
            username: None,
            playerid: None,
            serverid: None,

            token: "".to_string(),
            btoken: Cipher::new_128(&[0; 16]),
            authenticity: "".to_string(),
            authenticated: false,
        }
    }

    pub fn close(&mut self) {
        self.handle.abort();
        self.authenticated = false;
    }

    pub async fn set_identity(&mut self, uuid: Uuid) -> Result<(), String> {
        let response = utils::get_username(uuid, &self.hclient).await;
        if response.is_err() {
            return Err(response.err().unwrap());
        }

        self.username = Some(response.unwrap());
        self.uuid = Some(uuid);
        Ok(())
    }
}

impl Drop for Session {
    fn drop(&mut self) {
        self.close();
    }
}
