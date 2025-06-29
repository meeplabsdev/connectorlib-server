from typing import Any

from messages.BaseHandler import BaseHandler


class PlayerMovement(BaseHandler):
    async def act(
        self,
        sneaking: bool = False,
        sprinting: bool = False,
        swimming: bool = False,
        crawling: bool = False,
        onGround: bool = False,
        fallFlying: bool = False,
        velocity: list[float] = [0, 0, 0],
        **kwargs: list[Any],
    ) -> dict[str, Any] | None:
        if self.ws.session is None:
            return None
