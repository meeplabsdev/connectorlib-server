use std::path::Path;

pub fn is_docker() -> bool {
    Path::new("/.dockerenv").exists()
}
