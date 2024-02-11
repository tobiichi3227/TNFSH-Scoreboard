import aiohttp


timeout = aiohttp.ClientTimeout(total=20)
client_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5), timeout=timeout)


class Service:
    pass


def init_service():
    import utils
    from services.login import LoginService

    utils.logger.info("Service Init")

    Service.Login = LoginService()
