import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import update_password


class ResetPasswordHandler(RequestHandler):

    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        await self.render("reset-password.html")

    @reqenv
    async def post(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        reqtype = self.get_argument("reqtype")
        if reqtype == "reset":
            current_pw = self.get_argument("current_pw")
            new_pw = self.get_argument("new_pw")
            confirm_new_pw = self.get_argument("confirm_new_pw")

            err, msg = await update_password(self.session.session_id, current_pw, new_pw, confirm_new_pw)
            if err != Errors.Success:
                await self.error(err)
                return

            await self.finish(msg)
