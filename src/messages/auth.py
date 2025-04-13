import hashlib
import uuid as m_uuid
from datetime import datetime

import requests

from definitions import Player
from messages.base import BaseHandler

KEY = "thisIsATestKey!"

inProgress = []


class IdentityRequest(BaseHandler):
    async def act(self, uuid=None, username=None, **kwargs):
        if uuid is None or username is None:
            return None

        player_data: requests.Response = requests.get(f"https://api.minetools.eu/uuid/{username}")
        player_data: dict = player_data.json()

        if uuid.replace("-", "") != player_data.get("id", ""):
            return None

        nonce = m_uuid.uuid4().hex
        expect = hashlib.sha256(f"{nonce}{KEY}".encode("utf-8")).hexdigest()
        inProgress.append({"username": username, "uuid": uuid, "expect": expect, "begun": datetime.now()})

        for p in inProgress:
            if (datetime.now() - p["begun"]).total_seconds() > 12:
                inProgress.remove(p)

        return {
            "nonce": nonce,
            "uuid": uuid,
            "id": "IdentityChallenge",
        }


class IdentityChallenge(BaseHandler):
    async def act(self, uuid=None, result=None, **kwargs):
        if uuid is None or result is None:
            return {}

        for p in inProgress:
            if p["uuid"] == uuid and p["expect"] == result:
                session = m_uuid.uuid4().hex
                self.datastore.sessions.append(session)
                inProgress.remove(p)

                player: Player = Player(self.websocket, uuid, p["username"])
                self.datastore.add_player(player)
                self.websocket.player = player

                return {
                    "session": session,
                    "id": "IdentitySession",
                }
