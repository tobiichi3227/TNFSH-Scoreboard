import json
import time
import base64

import config
from utils.validate import get_validate_code
from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_student_info, get_validate_pic
from services.login import LoginService, LoginPayload


class LoginHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is not None:
            await self.finish("""
            你已經登入了
            <script>
                setTimeout(() => {
                    route.go('/board/info/');
                }, 1500);
            </script> 
            """)
            return

        await self.render("login.html")

    @reqenv
    async def post(self):
        reqtype = self.get_argument("reqtype")
        if reqtype == "login" and self.session is None:
            username = self.get_argument("username")
            password = self.get_argument("password")
            validate_code = self.get_argument("validate_code")
            validate_src = self.get_argument("validate_src")
            using_ocr = self.get_argument("using_ocr")

            if using_ocr == "true":
                err, res = await get_validate_pic()
                if err != Errors.Success:
                    await self.error(err)

                validate_src: str = res["src"]
                validate_pic: str = res["picture"]

                # Remove "data:image/jpeg;base64," from picture base64 encoded string
                validate_pic = validate_pic[validate_pic.find(",") + 1:]
                validate_code = get_validate_code(base64.b64decode(validate_pic))

            if len(validate_code) > 4:
                await self.error(Errors.WrongValidateCode)
                return

            err, form_token = await LoginService.inst.get_form_token()
            if err != Errors.Success:
                pass

            payload = LoginPayload(
                login_id=username,
                password=password,
                validate_code=validate_code,
                validate_src=validate_src,
                form_token=form_token,
                sch_no=config.SCHNO
            )

            err, session_id = await LoginService.inst.get_session_key(payload)

            need_reset_pw = False
            if err == Errors.NeedResetPassword:
                need_reset_pw = True

            elif err != Errors.Success:
                await self.error(err)
                return

            err, info = await get_student_info(session_id)
            if err != Errors.Success:
                await self.error(err)
                return

            self.setup_cookies(session_id, str(info["studentId"]), info["name"])

            if need_reset_pw:
                await self.error(Errors.NeedResetPassword)
            else:
                await self.success()

        elif reqtype == "logout":
            self.remove_cookies()
            await self.success()

    def setup_cookies(self, session_id: str, student_id: str, student_name: str):
        COOKIE_ARGS = {
            "expires": 30 * 60 + time.time(),  # https://www.cnblogs.com/apexchu/p/4363250.html
            "path": "/board",
            "httponly": True,
        }

        self.set_secure_cookie("session_id", session_id, **COOKIE_ARGS)
        self.set_secure_cookie("student_id", student_id, **COOKIE_ARGS)
        self.set_secure_cookie("student_name", student_name, **COOKIE_ARGS)

    def remove_cookies(self):
        self.clear_cookie("session_id", path="/board")
        self.clear_cookie("student_id", path="/board")
        self.clear_cookie("student_name", path="/board")


class ValidateHandler(RequestHandler):
    async def get(self):
        err, res = await get_validate_pic()
        if err != Errors.Success:
            await self.error(err)
            return

        await self.finish(json.dumps(res))
