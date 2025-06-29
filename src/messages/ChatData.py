import re

from typing import Any
import uuid

from messages.BaseHandler import BaseHandler


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
