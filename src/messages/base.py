from definitions import DataStore, Player


class BaseHandler:
    datastore: DataStore
    player: Player = None
    session: str = ""

    def __init__(self, datastore: DataStore, websocket, session):
        self.datastore = datastore
        self.websocket = websocket

        try:
            self.player = self.websocket.player
        except Exception as _:
            self.player = None

        if len(session) >= 32 and session in datastore.sessions:
            self.session = session

    async def act(self, **kwargs):
        return None
