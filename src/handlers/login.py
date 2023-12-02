import json

import const
import config
from utils.error import Success, RemoteServerError, WrongValidateCodeError
from handlers.base import RequestHandler, reqenv
from services.service import client_session
from services.api import get_student_info
from services.login import LoginService, LoginPayload
from services.session import SessionService


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

            if len(validate_code) > 4:
                await self.error(WrongValidateCodeError)
                return

            err, form_token = await LoginService.inst.get_form_token()
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

            err, session_key = await LoginService.inst.get_session_key(payload)
            if err != Success:
                await self.error(err)
                return

            err, info = await get_student_info(session_key)
            if err != Success:
                await self.error(err)
                return

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
        async with client_session.post(const.VALIDATE_URL) as resp:
            if not resp.ok:
                await self.error(RemoteServerError)
                return

            res = await resp.json()
            await self.finish(json.dumps({
                "picture": res["src"],
                "src": res["validateSrc"],
            }))
