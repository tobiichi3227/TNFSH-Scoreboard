from handlers.base import RequestHandler, reqenv


class IndexHandler(RequestHandler):
    @reqenv
    async def get(self):
        await self.render("index.html")


class AboutHandler(RequestHandler):
    @reqenv
    async def get(self):
        await self.render("about.html")


class InfoHandler(RequestHandler):
    @reqenv
    async def get(self):
        await self.render("info.html")
