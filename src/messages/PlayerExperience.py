from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerExperience(BaseHandler):
    async def act(
        self,
        level: int = 0,
        progress: float = 0,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
