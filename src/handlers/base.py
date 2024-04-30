from enum import Enum
from typing import Any

import tornado.template
import tornado.web

from services.session import Session


class Errors(Enum):
    General = "E"
    Success = "S"
    Exist = "Eexist"
    NotExist = "Enoext"
    WrongPasswordOrAccount = "Ewrongpwacct"
    WrongValidateCode = "Ewrongvalidatecode"
    WrongTooManyTimes = "Ewrongtoomany"
    NeedResetPassword = "Eneedresetpw"
    WrongParam = "Eparam"
    RemoteServer = "Eremote"
    RemoteServerBlock = "Eremoteblock"
    Unknown = "Eunk"


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tpldr = tornado.template.Loader("static/template", autoescape=None)

    async def render(self, templ: str, **kwargs):
        session = None
        session_id = self.get_secure_cookie("session_id")
        student_id = self.get_secure_cookie("student_id")
        student_name = self.get_secure_cookie("student_name")
        student_class_number = self.get_secure_cookie("student_class_number")
        student_seat_number = self.get_secure_cookie("student_seat_number")

        if session_id is not None:
            session_id = session_id.decode("utf-8")
            student_id = student_id.decode("utf-8")
            student_name = student_name.decode("utf-8")
            student_class_number: int = int(student_class_number.decode("utf-8"))
            student_seat_number: int = int(student_seat_number.decode("utf-8"))
            session = Session(session_id, int(student_id), student_name,
                              student_class_number, student_seat_number)

        if session is None:
            session = Session.Empty_Session

        kwargs["session"] = session

        assert templ is not None, "Missing templ argument"
        data = self.tpldr.load(templ).generate(**kwargs)

        await self.finish(data)

    async def error(self, err: Errors):
        await self.finish(str(err.value))

    async def success(self):
        await self.finish(str(Errors.Success.value))

    async def render_remote_server_err(self):
        await self.render("remote-server-error.html")


def reqenv(func):
    async def wrap(self, *args, **kwargs):
        self.session = None
        session_id = self.get_secure_cookie("session_id")
        student_id = self.get_secure_cookie("student_id")
        student_name = self.get_secure_cookie("student_name")
        student_class_number = self.get_secure_cookie("student_class_number")
        student_seat_number = self.get_secure_cookie("student_seat_number")

        if session_id is not None:
            session_id = session_id.decode("utf-8")
            student_id = student_id.decode("utf-8")
            student_name = student_name.decode("utf-8")
            student_class_number: int = int(student_class_number.decode("utf-8"))
            student_seat_number: int = int(student_seat_number.decode("utf-8"))
            self.session = Session(session_id, int(student_id), student_name,
                                   student_class_number, student_seat_number)

        ret = await func(self, *args, **kwargs)
        return ret

    return wrap
