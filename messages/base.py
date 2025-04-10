from definitions import DataStore, Player


class BaseHandler:
    datastore: DataStore
    player: Player = None
    session: str = ""

    def __init__(self, datastore: DataStore, websocket, session):
        self.datastore = datastore
        self.websocket = websocket

        if len(session) >= 32 and session in datastore.sessions:
            self.session = session

    async def act(self, **kwargs):
        return None
