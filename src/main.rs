use std::net::SocketAddr;
use tokio::net::{ TcpListener, TcpStream };
use tokio_tungstenite::{ accept_async, tungstenite::{ Bytes, Message } };
use futures_util::{ SinkExt, StreamExt };
use paris::*;

mod messages;
mod handlers;
mod session;
mod utils;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:3000").await?;
    success!("Server started on :3000");

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

    while let Some(msg) = read.next().await {
        match msg {
            Ok(Message::Binary(data)) => {
                if !sess.is_authenticated() {
                    match rmp_serde::from_slice::<handlers::SocketMessage>(&data) {
                        Ok(msg) => {
                            info!("<d>({} → me)</d> {:?}", addr, msg);

                            let response = handlers::handle(msg, &mut sess);
                            if let Some(res) = response {
                                let buf = rmp_serde
                                    ::to_vec::<handlers::SocketResponse>(&res)
                                    .unwrap();
                                write.send(Message::Binary(Bytes::from(buf))).await.unwrap();

                                info!("<d>(me → {})</d> {:?}", addr, res);
                            }
                        }
                        Err(e) => {
                            error!("<on red>Error: {}</>", e);
                        }
                    }
                } else {
                    warn!("authgenticated session message");
                }
            }
            Ok(Message::Close(_)) => {
                break;
            }
            _ => {}
        }
    }
}
