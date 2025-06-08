import hashlib
from typing import Any, cast
import uuid as m_uuid
from datetime import datetime

# import requests

from messages.base import BaseHandler

KEY = "thisIsATestKey!"

inProgress: list[dict[str, str | datetime]] = []


class IdentityRequest(BaseHandler):
    async def act(
        self,
        uuid: str | None = None,
        username: str | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if uuid is None or username is None:
            return None

        # TODO: check UUID
        # player_data: dict[str, str] = requests.get(f"https://api.minetools.eu/uuid/{username}").json()
        # if uuid.replace("-", "") != player_data.get("id", ""):
        #     return None

        nonce = m_uuid.uuid4().hex
        expect = hashlib.sha256(f"{nonce}{KEY}".encode("utf-8")).hexdigest()
        inProgress.append({"username": username, "uuid": uuid, "expect": expect, "begun": datetime.now()})

        for p in inProgress:
            begun: datetime = cast(datetime, p["begun"])
            if (datetime.now() - begun).total_seconds() > 12:
                inProgress.remove(p)

        return {
            "nonce": nonce,
            "uuid": uuid,
            "id": "IdentityChallenge",
        }


class IdentityChallenge(BaseHandler):
    async def act(
        self,
        uuid: str | None = None,
        result: str | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if uuid is None or result is None:
            return None

        match: dict[str, str | datetime] | None = next((p for p in inProgress if p["uuid"] == uuid and p["expect"] == result), None)
        if match:
            session = m_uuid.uuid4().hex
            player = self.ws.de.Player(
                self.ws.db,
                m_uuid.UUID(hex=uuid.replace("-", "")),
                str(match["username"]),
            )

            self.ws.session = self.ws.de.Session(
                self.ws.db,
                session,
                player,
            )
            inProgress.remove(match)

            return {
                "session": session,
                "id": "IdentitySession",
            }
