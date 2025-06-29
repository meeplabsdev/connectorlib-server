from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerArmor(BaseHandler):
    async def act(
        self,
        protectionLevel: int = 0,
        slots: dict[str, str] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
