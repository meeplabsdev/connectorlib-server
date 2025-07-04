use std::net::SocketAddr;
use rmp_serde::Serializer;
use serde::Serialize;
use tokio::net::{ TcpListener, TcpStream };
use tokio_tungstenite::{ accept_async, tungstenite::{ Bytes, Message } };
use futures_util::{ SinkExt, StreamExt };

mod messages;
mod handlers;
mod session;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:3000").await?;
    println!("Server started on :3000");

    loop {
        let (stream, addr) = listener.accept().await?;

        tokio::spawn(async move { handle(stream, addr).await });
    }
}

async fn handle(stream: TcpStream, addr: SocketAddr) {
    let ws_stream = match accept_async(stream).await {
        Ok(ws) => ws,
        Err(e) => {
            println!("({}) |- Failed {}", addr, e);
            return;
        }
    };

    let (mut write, mut read) = ws_stream.split();
    println!("({}) |- Connection Established", addr);
    let sess: session::Session = session::Session::new();

    while let Some(msg) = read.next().await {
        match msg {
            Ok(Message::Binary(data)) => {
                match rmp_serde::from_slice::<handlers::SocketMessage>(&data) {
                    Ok(msg) => {
                        println!("({}) |← {:?}", addr, msg);

                        let response = handlers::handle(msg, &sess);
                        if let Some(res) = response {
                            let buf = rmp_serde::to_vec::<handlers::SocketResponse>(&res).unwrap();
                            write.send(Message::Binary(Bytes::from(buf))).await.unwrap();

                            println!("({}) |→ {:?}", addr, res);
                        }
                    }
                    Err(e) => {
                        println!("({}) Error: {}", addr, e);
                    }
                }
            }
            Ok(Message::Close(_)) => {
                println!("({}) |- Connection Closed", addr);
                break;
            }
            _ => {}
        }
    }
}
