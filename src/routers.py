import tornado.web

from handlers.index import IndexHandler, AboutHandler, InfoHandler, PWAInstallationHandler, ManifestHandler
from handlers.login import LoginHandler, ValidateHandler
from handlers.resetpw import ResetPasswordHandler
from handlers.exam import ExamHandler
from handlers.term import TermHandler
from handlers.reward import RewardHandler
from handlers.absence import SubjectAbsenceCountHandler, AbsenceHandler
from handlers.graduation import GraduationCreditsHandler
from handlers.forgetpw import ForgetPasswordHandler
from handlers.leave import LeaveRequestHandler


def get_routers():
    return [
        ("/be/info", InfoHandler),
        ("/be/about", AboutHandler),
        ("/be/installation", PWAInstallationHandler),
        ("/be/manifest.json", ManifestHandler),

        ("/be/login", LoginHandler),
        ("/be/validate", ValidateHandler),
        ("/be/resetpw", ResetPasswordHandler),
        ("/be/forgetpw", ForgetPasswordHandler),

        ("/be/exam", ExamHandler),
        ("/be/term", TermHandler),
        ("/be/reward", RewardHandler),
        ("/be/absence", AbsenceHandler),
        ("/be/subjectabsence", SubjectAbsenceCountHandler),
        ("/be/graduation", GraduationCreditsHandler),
        ("/be/leave", LeaveRequestHandler),

        (r"/src/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
        ("/.*", IndexHandler),

    ]
