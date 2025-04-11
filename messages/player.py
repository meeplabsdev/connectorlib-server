from messages.base import BaseHandler


class PlayerJoin(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        return None


class PlayerQuit(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        return None


class PlayerRespawn(BaseHandler):
    async def act(self, ip=None, uuid=None, **kwargs):
        return None


class PlayerAdvancement(BaseHandler):
    async def act(self, ip=None, uuid=None, advancement=None, **kwargs):
        return None
