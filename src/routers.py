from handlers.index import IndexHandler, AboutHandler, InfoHandler
from handlers.login import LoginHandler, ValidateHandler
from handlers.exam import ExamHandler


def get_routers():
    return [
        ('/index', IndexHandler),
        ('/info', InfoHandler),
        # ('/news'),
        ('/about', AboutHandler),

        ('/login', LoginHandler),
        ('/validate', ValidateHandler),
        ('/exam', ExamHandler),
        # ('/studentcard'),
    ]
