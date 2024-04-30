from handlers.base import RequestHandler, reqenv, Errors
from services.api import forget_password


class ForgetPasswordHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is not None:
            return

        await self.render("forget-password.html")

    @reqenv
    async def post(self):
        if self.session is not None:
            return

        reqtype = self.get_argument("reqtype")
        if reqtype == "forget":
            acct = self.get_argument("account")
            name = self.get_argument("name")
            idno = self.get_argument("idno")
            birth = self.get_argument("birth")

            err, msg = await forget_password(acct, name, idno, birth)
            if err != Errors.Success:
                await self.error(err)
                return

            await self.finish(msg)
