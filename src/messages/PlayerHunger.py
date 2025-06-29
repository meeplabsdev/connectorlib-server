from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerHunger(BaseHandler):
    async def act(
        self,
        hunger: int = 0,
        saturation: int = 0,
        exhaustion: int = 0,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
