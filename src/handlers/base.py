import tornado.template
import tornado.web

from services.session import Session
from utils.error import Success


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tpldr = tornado.template.Loader("static/template", autoescape=None)

    async def render(self, templ: str, **kwargs):
        session = None
        session_id = self.get_secure_cookie("session_id")
        student_id = self.get_secure_cookie("student_id")
        student_name = self.get_secure_cookie("student_name")

        if session_id is not None:
            session_id = session_id.decode("utf-8")
            student_id = student_id.decode("utf-8")
            student_name = student_name.decode("utf-8")
            session = Session(session_id, int(student_id), student_name)

        if session is None:
            session = Session.Empty_Session

        kwargs["session"] = session

        assert templ is not None, "Missing templ argument"
        data = self.tpldr.load(templ).generate(**kwargs)

        await self.finish(data)

    async def error(self, err):
        await self.finish(str(err))

    async def success(self):
        await self.finish(str(Success))


def reqenv(func):
    async def wrap(self, *args, **kwargs):
        self.session = None
        session_id = self.get_secure_cookie("session_id")
        student_id = self.get_secure_cookie("student_id")
        student_name = self.get_secure_cookie("student_name")

        if session_id is not None:
            session_id = session_id.decode("utf-8")
            student_id = student_id.decode("utf-8")
            student_name = student_name.decode("utf-8")
            self.session = Session(session_id, student_id, student_name)

        ret = await func(self, *args, **kwargs)
        return ret

    return wrap
