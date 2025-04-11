import aiohttp

import asyncio
from services.cache import CacheService

timeout = aiohttp.ClientTimeout(total=20)
async def create_session():
    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5, ssl=False), timeout=timeout)
client_session = asyncio.get_event_loop().run_until_complete(create_session())


class Service:
    pass


def init_service():
    import utils
    from services.login import LoginService

    utils.logger.info("Service Init")

    Service.Login = LoginService()
    Service.Cache = CacheService()
