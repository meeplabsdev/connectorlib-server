use std::fs;
use std::path::Path;

fn main() {
    println!("cargo:rerun-if-changed=src/messages");

    let messages_dir = Path::new("src/messages");
    if !messages_dir.exists() {
        return;
    }

    let mut mod_contents = String::new();
    let mut handlers_contents = String::new();

    mod_contents.push_str("#![allow(non_snake_case)]\n");
    handlers_contents.push_str(
        "use serde::{ Deserialize, Serialize };\n\n\
                use crate::messages::*;\n\
                use crate::session::Session;\n\n\
                #[derive(Deserialize, Debug)]\n\
                #[serde(tag = \"id\", content = \"value\")]\n\
                pub enum SocketMessage {\n"
    );

    let entries = fs::read_dir(messages_dir).expect("Failed to read messages directory");
    let mut module_names = Vec::new();

    for entry in entries {
        let entry = entry.expect("Failed to read directory entry");
        let path = entry.path();
        if !path.is_file() || path.file_name() == Some(std::ffi::OsStr::new("mod.rs")) {
            continue;
        }

        if let Some(extension) = path.extension() {
            if extension == "rs" {
                if let Some(file_stem) = path.file_stem() {
                    if let Some(module_name) = file_stem.to_str() {
                        module_names.push(module_name.to_string());
                    }
                }
            }
        }
    }

    module_names.sort();
    for module_name in module_names.clone() {
        mod_contents.push_str(&format!("pub mod {};\n", module_name));
        handlers_contents.push_str(&format!("    {m}({m}::Message),\n", m = module_name));
    }

    handlers_contents.push_str(
        "}\n\n\
                #[derive(Serialize, Debug)]\n\
                #[serde(tag = \"id\", content = \"value\")]\n\
                pub enum SocketResponse {\n"
    );

    for module_name in module_names.clone() {
        handlers_contents.push_str(&format!("    {m}({m}::Response),\n", m = module_name));
    }

    handlers_contents.push_str(
        "}\n\n\
        pub fn handle(message: SocketMessage, sess: &Session) -> Option<SocketResponse> {
    match message {\n"
    );

    for module_name in module_names.clone() {
        handlers_contents.push_str(
            &format!(
                "        SocketMessage::{m}(msg) => {m}::handle(msg, sess),\n",
                m = module_name
            )
        );
    }

    handlers_contents.push_str("    }\n}\n");

    let mod_file_path = messages_dir.join("mod.rs");
    fs::write(&mod_file_path, mod_contents).expect("Failed to write mod.rs file");

    let handlers_file_path = Path::new("src").join("handlers.rs");
    fs::write(&handlers_file_path, handlers_contents).expect("Failed to write handlers.rs file");
}
