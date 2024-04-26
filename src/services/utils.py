from handlers.base import Errors
from services.api import ReturnType


def timeout_handle(func):
    async def wrapper(*args, **kwargs):
        try:
            ret: ReturnType = await func(*args, **kwargs)
        except TimeoutError:
            ret = Errors.RemoteServer, None

        return ret

    return wrapper
