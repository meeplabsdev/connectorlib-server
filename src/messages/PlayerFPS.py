from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerFPS(BaseHandler):
    async def act(
        self,
        fps: int = 0,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
