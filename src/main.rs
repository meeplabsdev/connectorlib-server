use futures_util::{SinkExt, StreamExt};
use paris::*;
use std::net::SocketAddr;
use tokio::net::{TcpListener, TcpStream};
use tokio_tungstenite::{
    accept_async,
    tungstenite::{Bytes, Message},
};

mod handlers;
mod messages;
mod session;
mod utils;

const DEV: bool = false;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:3740").await?;
    success!("Server started on :3740");

    loop {
        let (stream, addr) = listener.accept().await?;
        tokio::spawn(async move { client(stream, addr).await });
    }
}

async fn client(stream: TcpStream, addr: SocketAddr) {
    let ws_stream = match accept_async(stream).await {
        Ok(ws) => ws,
        Err(e) => {
            error!("<d>({})</d> Failed {}", addr, e);
            return;
        }
    };

    let (mut write, mut read) = ws_stream.split();
    let mut sess: session::Session = session::Session::new().await;

    info!("<d>({})</d> Connected", addr);

    while let Some(msg) = read.next().await {
        sess.limiter.until_ready().await;
        match msg {
            Ok(Message::Binary(data)) => {
                if !sess.authenticated {
                    handle(addr, &mut write, &mut sess, data).await;
                } else {
                    if data.len() <= 16 {
                        continue;
                    }

                    let iv = &data[..16];
                    let encrypted = &data[16..];
                    let decrypted = sess.btoken.cbc_decrypt(iv, encrypted);
                    handle(addr, &mut write, &mut sess, Bytes::from(decrypted)).await;
                }
            }
            Ok(Message::Close(_)) => {
                sess.close();
            }
            _ => {}
        }
    }
}

async fn handle(
    addr: SocketAddr,
    write: &mut futures_util::stream::SplitSink<
        tokio_tungstenite::WebSocketStream<TcpStream>,
        Message,
    >,
    sess: &mut session::Session,
    data: Bytes,
) {
    match rmp_serde::from_slice::<handlers::SocketMessage>(&data) {
        Ok(msg) => {
            info!("<d>({} → me)</d> {:?}", addr, msg);

            let response = handlers::handle(msg, sess);
            if let Some(res) = response.await {
                let buf = rmp_serde::to_vec::<handlers::SocketResponse>(&res).unwrap();
                write.send(Message::Binary(Bytes::from(buf))).await.unwrap();

                info!("<d>(me → {})</d> {:?}", addr, res);
            }
        }
        Err(e) => {
            error!("<on red>Error: {}</>", e);
        }
    }
}
