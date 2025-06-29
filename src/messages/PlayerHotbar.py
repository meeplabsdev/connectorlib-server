from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerHotbar(BaseHandler):
    async def act(
        self,
        selectedSlot: int = 0,
        slots: dict[str, str] = {},
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
