use uuid::Uuid;

#[allow(dead_code)]
pub struct Session {
    uuid: Option<Uuid>,
    username: Option<String>,

    token: String,
    authenticity: String,
    authenticated: bool,
}

impl Session {
    pub fn new() -> Self {
        Self {
            uuid: None,
            username: None,

            token: "".to_string(),
            authenticity: "".to_string(),
            authenticated: false,
        }
    }

    pub fn set_identity(&mut self, uuid: Uuid, username: String) {
        self.uuid = Some(uuid);
        self.username = Some(username);
    }

    pub fn get_identity(&self) -> Option<(Uuid, String)> {
        if self.uuid.is_none() || self.username.is_none() {
            return None;
        }

        return Some((self.uuid.unwrap(), self.username.clone().unwrap()));
    }

    pub fn set_authenticity(&mut self, authenticity: String) {
        self.authenticity = authenticity;
    }

    pub fn is_authenticity(&self, authenticity: String) -> bool {
        return self.authenticity.eq(&authenticity);
    }

    pub fn authenticate(&mut self, token: String) {
        self.token = token;
        self.authenticated = true;
    }
}
