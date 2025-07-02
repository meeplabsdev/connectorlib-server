use uuid::Uuid;

pub struct Session {
    pub uuid: Option<Uuid>,
    pub username: Option<String>,
}
