from handlers.index import IndexHandler, AboutHandler, InfoHandler, PWAInstallationHandler
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
        ("/index", IndexHandler),
        ("/info", InfoHandler),
        # ('/news'),
        ("/about", AboutHandler),
        ("/installation", PWAInstallationHandler),

        ("/login", LoginHandler),
        ("/validate", ValidateHandler),
        ("/resetpw", ResetPasswordHandler),
        ("/forgetpw", ForgetPasswordHandler),
        ("/leave", LeaveRequestHandler),

        ("/exam", ExamHandler),
        ("/term", TermHandler),
        ("/reward", RewardHandler),
        ("/absence", AbsenceHandler),
        ("/subjectabsence", SubjectAbsenceCountHandler),
        ("/graduation", GraduationCreditsHandler),
        # ('/studentcard'),
    ]
