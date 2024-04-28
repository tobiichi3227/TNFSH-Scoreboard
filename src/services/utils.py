from typing import Any

from handlers.base import Errors

ReturnType = tuple[Errors, Any]


def timeout_handle(func):
    async def wrapper(*args, **kwargs):
        try:
            ret: ReturnType = await func(*args, **kwargs)
        except TimeoutError:
            ret = Errors.RemoteServer, None

        return ret

    return wrapper
