import json
import base64

import config
from utils.error import Success, WrongValidateCodeError
from utils.validate import get_validate_code
from handlers.base import RequestHandler, reqenv
from services.api import get_student_info, get_validate_pic
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
            using_ocr = self.get_argument("using_ocr")

            if using_ocr == "true":
                err, res = await get_validate_pic()
                if err != Success:
                    await self.error(err)

                validate_src: str = res["src"]
                validate_pic: str = res["picture"]

                # Remove "data:image/jpeg;base64," from picture base64 encoded string
                validate_pic = validate_pic[validate_pic.find(",") + 1:]
                validate_code = get_validate_code(base64.b64decode(validate_pic))

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
        err, res = await get_validate_pic()
        if err != Success:
            await self.error(err)
            return

        await self.finish(json.dumps(res))
