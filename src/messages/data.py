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
        x: int | None = None,
        y: int | None = None,
        z: int | None = None,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None or x is None or y is None or z is None:
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
            x,
            y,
            z,
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
        sender: str = "",
        recipient: str = "Global Chat",
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        content = self.extract_content(message, sender)
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
            uuid.UUID(int=1),
            uuid.UUID(int=1),
        )
        # TODO: figure out how to find the UUID for sender and recipient, will need to modify client side message


class SystemChatData(BaseHandler):
    async def act(
        self,
        ip: str = "Unknown",
        message: str = "",
        recipient: str = "Global Chat",
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None

        return None
        # temporary disable

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
            uuid.UUID(int=1),
            uuid.UUID(int=1),
        )
        # TODO: figure out how to find the UUID for sender and recipient, will need to modify client side message
