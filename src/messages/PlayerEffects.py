from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerEffects(BaseHandler):
    async def act(
        self,
        effects: dict[str, int] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
