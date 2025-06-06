from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from websocket import Websocket


class BaseHandler:
    def __init__(self, websocket: "Websocket") -> None:
        self.ws = websocket

    async def act(self, **kwargs: list[Any]) -> dict[str, Any] | None:
        return None
