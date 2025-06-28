import re

from datetime import datetime, timezone
from typing import Any
import uuid

from messages.base import BaseHandler


class NetworkData(BaseHandler):
    async def act(
        self,
        ip: str = "",
        user_agent: str = "",
        _encoding: str = "",
        _mime: str = "",
        via: str = "",
        forwarded: str = "",
        _language: str = "",
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        self.ws.de.NetworkData(
            self.ws.db,
            self.ws.session.player,
            ip,
            user_agent,
            via,
            forwarded.split(","),
        )


class PositionData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        dimension: str = "",
        pos: list[int] | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or pos is None or len(pos) != 3:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        s_player = self.ws.de.ServerPlayer(
            self.ws.db,
            self.ws.session.player,
            server,
        )
        # TODO: update the last seen of the server_player and player
        self.ws.de.Location(
            self.ws.db,
            s_player,
            self.ws.de.Dimension(self.ws.db, dimension),
            pos[0],
            pos[1],
            pos[2],
        )
        # TODO: update the last seen of the location


class ChatData(BaseHandler):
    def extract_content(self, message: str, sender: str):
        # <sender> / [sender] / [<sender>]
        match = re.match(rf"^[\[\<]?{re.escape(sender)}[\]\>]?\s*(.*)", message)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # "NAME whispers to you: CONTENT"
        match = re.match(r"^whispers to you:\s*(.*)", message)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # You whisper to NAME: CONTENT
        match = re.match(rf"^[Yy]ou.*?{re.escape(sender)}.*?:\s*(.*)", message)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # NAME: CONTENT
        match = re.match(rf"^{re.escape(sender)}.*?:\s*(.*)", message)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # Colon-delimited
        if ":" in message:
            content = message.split(":", 1)[1].strip()
            if content:
                return content

        # Fallback: sender found in message, get rest
        words = message.split()
        sender_words = sender.split()
        for i in range(len(words)):
            if words[i : i + len(sender_words)] == sender_words:
                content = " ".join(words[i + len(sender_words) :]).strip()
                if content:
                    return content

        return message.strip()

    async def act(
        self,
        ip: str = "Unknown",
        message: str = "",
        sender: dict[str, str] = {},
        recipient: dict[str, str] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        content = self.extract_content(message, list(sender.keys())[0])
        server = self.ws.de.Server(self.ws.db, ip, ip)
        s_player = self.ws.de.ServerPlayer(
            self.ws.db,
            self.ws.session.player,
            server,
        )

        self.ws.de.Message(
            self.ws.db,
            s_player,
            content,
            uuid.UUID(list(sender.values())[0]),
            uuid.UUID(list(recipient.values())[0]),
        )
        # TODO: switch the uuids for player ids


class SystemChatData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        message: str = "",
        recipient: dict[str, str] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        server = self.ws.de.Server(self.ws.db, ip, ip)
        s_player = self.ws.de.ServerPlayer(
            self.ws.db,
            self.ws.session.player,
            server,
        )

        self.ws.de.Message(
            self.ws.db,
            s_player,
            message,
            uuid.UUID(int=0),
            uuid.UUID(list(recipient.values())[0]),
        )
