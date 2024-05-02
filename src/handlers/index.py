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

class PWAInstallationHandler(RequestHandler):
    @reqenv
    async def get(self):
        await self.render("pwa-installation-guide.html")
