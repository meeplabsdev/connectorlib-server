use uuid::Uuid;

#[allow(dead_code)]
pub struct Session {
    uuid: Option<Uuid>,
    username: Option<String>,
}

impl Session {
    pub fn new() -> Self {
        Self {
            uuid: None,
            username: None,
        }
    }
}
