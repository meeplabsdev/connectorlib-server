from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerBreath(BaseHandler):
    async def act(
        self,
        breath: int = 0,
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
