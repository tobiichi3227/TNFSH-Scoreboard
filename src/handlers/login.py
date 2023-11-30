import json
import requests

import const
import config
from handlers.base import RequestHandler, reqenv
from services.api import get_student_info
from services.login import LoginService, LoginPayload
from services.session import SessionService
from utils.error import Success


class LoginHandler(RequestHandler):
    @reqenv
    async def get(self):
        await self.render('login.html')

    @reqenv
    async def post(self):
        reqtype = self.get_argument("reqtype")
        if reqtype == "login":
            username = self.get_argument("username")
            password = self.get_argument("password")
            validate_code = self.get_argument("validate_code")
            validate_src = self.get_argument("validate_src")

            err, form_token = LoginService.inst.get_form_token()
            if err != Success:
                pass

            payload = LoginPayload(
                login_id=username,
                password=password,
                validate_code=validate_code,
                validate_src=validate_src,
                form_token=form_token,
                sch_no=config.SCHNO
            )

            err, session_key = LoginService.inst.get_session_key(payload)
            if err != Success:
                await self.error(err)
                return

            info = get_student_info(session_key)
            SessionService.inst.create_session(session_key, info["studentId"], info["name"])
            self.set_secure_cookie('session_id', session_key, path='/board', httponly=True)
            await self.success()

        elif reqtype == "logout":
            session_id = self.get_argument("session_id")
            err, _ = SessionService.inst.remove_session(session_id)

            if err != Success:
                pass

            self.clear_cookie('session_id', path='/board')
            await self.success()


class ValidateHandler(RequestHandler):

    async def get(self):
        # TODO: Post Error Handle
        res = requests.post(const.VALIDATE_URL).json()
        await self.finish(json.dumps({
            "picture": res["src"],
            "src": res["validateSrc"],
        }))
