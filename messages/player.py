from definitions import Server
from messages.base import BaseHandler


class PlayerJoin(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        sPlayer = None
        for p in server.players:
            if p.player.uuid == uuid:
                sPlayer = p
                break

        if sPlayer is None:
            return

        sPlayer.add_chat(f"(JOINED){uuid}")


class PlayerQuit(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        sPlayer = None
        for p in server.players:
            if p.player.uuid == uuid:
                sPlayer = p
                break

        if sPlayer is None:
            return

        sPlayer.add_chat(f"(LEFT){uuid}")


class PlayerRespawn(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        sPlayer = None
        for p in server.players:
            if p.player.uuid == uuid:
                sPlayer = p
                break

        if sPlayer is None:
            return

        sPlayer.add_chat(f"(RESPAWNED){uuid}")


class PlayerAdvancement(BaseHandler):
    async def act(self, ip=None, uuid=None, advancement=None, **kwargs):
        if self.session is None or self.session == "":
            return None

        server: Server = Server(self.websocket, ip)
        self.datastore.add_server(server)

        server = None
        for s in self.datastore.servers:
            if s.ip == ip:
                server = s

        if server is None:
            return

        sPlayer = None
        for p in server.players:
            if p.player.uuid == uuid:
                sPlayer = p
                break

        if sPlayer is None:
            return

        sPlayer.add_advancement(advancement)
