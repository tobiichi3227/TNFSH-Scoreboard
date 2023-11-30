import utils
from services.session import SessionService
from services.login import LoginService


class Service:
    pass


def init_service():
    utils.logger.info("Service Init")

    Service.Session = SessionService()
    Service.Login = LoginService()
