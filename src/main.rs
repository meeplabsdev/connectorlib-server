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
            println!("(Failed) {}: {}", addr, e);
            return;
        }
    };

    let (mut write, mut read) = ws_stream.split();
    println!("(Connected) {}", addr);
    let sess: session::Session = session::Session::new();

    while let Some(msg) = read.next().await {
        match msg {
            Ok(Message::Binary(data)) => {
                match rmp_serde::from_slice::<handlers::SocketMessage>(&data) {
                    Ok(msg) => {
                        let response = handlers::handle(msg, &sess);
                        if let Some(response) = response {
                            let mut buf = Vec::new();
                            response.serialize(&mut Serializer::new(&mut buf)).unwrap();
                            let bytes = Bytes::from(buf);
                            write.send(Message::Binary(bytes)).await.unwrap();
                        }
                    }
                    Err(e) => {
                        println!("({}) Error: {}", addr, e);
                    }
                }
            }
            Ok(Message::Close(_)) => {
                println!("(Closed) {}", addr);
                break;
            }
            _ => {}
        }
    }
}
