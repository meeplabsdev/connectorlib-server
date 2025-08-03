FROM rust:latest AS build

RUN USER=root cargo new --bin connectorlib-server
WORKDIR /connectorlib-server

COPY ./Cargo.lock ./Cargo.lock
COPY ./Cargo.toml ./Cargo.toml
COPY ./build.rs ./build.rs
COPY ./src ./src

RUN cargo build --release && rm src/*.rs && rm ./target/release/deps/connectorlib*

FROM rust:slim-bookworm

RUN apt-get update && apt-get install -y libssl-dev
COPY --from=build /connectorlib-server/target/release/connectorlib-server .
COPY ./config.sql ./config.sql

CMD ["./connectorlib-server"]