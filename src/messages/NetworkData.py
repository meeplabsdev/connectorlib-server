from typing import Any

from messages.BaseHandler import BaseHandler


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
