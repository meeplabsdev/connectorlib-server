use std::net::SocketAddr;
use tokio::net::{ TcpListener, TcpStream };
use tokio_tungstenite::{ accept_async, tungstenite::{ Bytes, Message } };
use futures_util::{ SinkExt, StreamExt };
use colored::Colorize;

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
            println!("({}) {}", addr.to_string().bold(), format!("|- Failed {}", e).magenta());
            return;
        }
    };

    let (mut write, mut read) = ws_stream.split();
    println!("({}) |- Connection Established", addr.to_string().bold());
    let mut sess: session::Session = session::Session::new();

    while let Some(msg) = read.next().await {
        match msg {
            Ok(Message::Binary(data)) => {
                match rmp_serde::from_slice::<handlers::SocketMessage>(&data) {
                    Ok(msg) => {
                        println!("({}) {}", addr.to_string().bold(), format!("|← {:?}", msg).red());

                        let response = handlers::handle(msg, &mut sess);
                        if let Some(res) = response {
                            let buf = rmp_serde::to_vec::<handlers::SocketResponse>(&res).unwrap();
                            write.send(Message::Binary(Bytes::from(buf))).await.unwrap();

                            println!(
                                "({}) {}",
                                addr.to_string().bold(),
                                format!("|→ {:?}", res).blue()
                            );
                        }
                    }
                    Err(e) => {
                        println!(
                            "({}) {}",
                            addr.to_string().bold(),
                            format!("Error: {}", e).magenta()
                        );
                    }
                }
            }
            Ok(Message::Close(_)) => {
                println!("({}) |- Connection Closed", addr.to_string().bold());
                break;
            }
            _ => {}
        }
    }
}
