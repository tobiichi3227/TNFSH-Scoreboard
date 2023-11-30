import tornado.template
import tornado.web

from services.session import SessionService
from utils.error import Success


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tpldr = tornado.template.Loader("static/template", autoescape=None)

    async def render(self, templ: str, **kwargs):
        session_id = self.get_secure_cookie("session_id")
        session = None
        if session_id is not None:
            session_id = session_id.decode('utf-8')
            _, session = SessionService.inst.get_session(session_id)

        if session is None:
            session = SessionService.EmptySession

        kwargs['session'] = session

        if templ is not None:
            data = self.tpldr.load(templ).generate(**kwargs)
        else:
            raise AssertionError("args none")

        await self.finish(data)

    async def error(self, err):
        await self.finish(str(err))

    async def success(self):
        await self.finish(str(Success))


def reqenv(func):
    async def wrap(self, *args, **kwargs):
        self.session = None
        session_id = self.get_secure_cookie("session_id")
        if session_id is not None:
            session_id = session_id.decode('utf-8')
            err, flag = SessionService.inst.is_session_expire(session_id)
            if err != Success:
                self.clear_cookie('session_id', path='/board')

            elif flag:
                self.clear_cookie('session_id', path='/board')
                SessionService.inst.remove_session(session_id)

            else:
                err, session = SessionService.inst.get_session(session_id)
                self.session = session

        ret = await func(self, *args, **kwargs)
        return ret

    return wrap