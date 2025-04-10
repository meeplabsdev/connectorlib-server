from messages.base import BaseHandler


class NetworkData(BaseHandler):
    async def act(self, ip=None, user_agent=None, port=None, method=None, encoding=None, mime=None, via=None, forwarded=None, language=None, **kwargs):
        return None


class PositionData(BaseHandler):
    async def act(self, ip=None, x=None, y=None, z=None, **kwargs):
        return None


class DataRequest(BaseHandler):
    async def act(self, **kwargs):
        if self.session is None or self.session == "":
            return None

        response = {
            "id": "DataResponse",
        }

        response.update(self.datastore.dump())
        return response
