"""
    @author: tobiichi3227
    @day: 2023/10/23
"""
import time
import signal

import tornado.netutil
import tornado.web
import tornado.log
import tornado.options
import tornado.httpserver
import tornado.ioloop

from services import service
import config
import utils
import routers


class Server:
    def __init__(self):
        self.port = config.PORT
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.httpserver = None
        self.deadline = 0

    def server_init(self):
        utils.logger.info("Server Init")

        service.init_service()

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGQUIT, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

        httpsock = tornado.netutil.bind_sockets(self.port)

        tornado.log.enable_pretty_logging()

        tornado.options.parse_command_line()

        # for dev
        # app = tornado.web.Application(routers.get_routers(),
        #                               autoescape='xhtml_escape', cookie_secret=config.SECRET_COOKIE,
        #                               debug=True, autoreload=True)

        app = tornado.web.Application(routers.get_routers(),
                                      autoescape='xhtml_escape', cookie_secret=config.SECRET_COOKIE)
        self.httpserver = tornado.httpserver.HTTPServer(app, xheaders=True)
        self.httpserver.add_sockets(httpsock)

    def server_start(self):
        utils.logger.info("Server Start")

        self.ioloop.start()

    def server_shutdown(self):
        utils.logger.info("Stopping http server")

        if self.httpserver is not None:
            self.httpserver.stop()

        self.deadline = time.time() + 1
        self.stop_ioloop()

    def stop_ioloop(self):
        now = time.time()
        if now < self.deadline and self.ioloop.time:
            self.ioloop.add_timeout(now + 1, self.stop_ioloop)
        else:
            utils.logger.info("Server shutdown!")

            from services.service import client_session
            self.ioloop.run_in_executor(func=client_session.close, executor=None)
            self.ioloop.stop()

    def sig_handler(self, sig, _):
        utils.logger.info(f"Caught signal: {sig}")
        tornado.ioloop.IOLoop.current().add_callback_from_signal(self.server_shutdown)


if __name__ == "__main__":
    server = Server()
    server.server_init()
    server.server_start()
