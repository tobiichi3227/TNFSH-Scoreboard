from handlers.index import IndexHandler, AboutHandler, InfoHandler
from handlers.login import LoginHandler, ValidateHandler
from handlers.resetpw import ResetPasswordHandler
from handlers.exam import ExamHandler
from handlers.term import TermHandler
from handlers.reward import RewardHandler
from handlers.absence import AbsenceHandler


def get_routers():
    return [
        ("/index", IndexHandler),
        ("/info", InfoHandler),
        # ('/news'),
        ("/about", AboutHandler),

        ("/login", LoginHandler),
        ("/validate", ValidateHandler),
        ("/resetpw", ResetPasswordHandler),

        ("/exam", ExamHandler),
        ("/term", TermHandler),
        ("/reward", RewardHandler),
        ("/absence", AbsenceHandler),
        # ('/studentcard'),
    ]
