from utils.error import RemoteServerError, ReturnType


def timeout_handle(func):
    async def wrapper(*args, **kwargs):
        try:
            ret: ReturnType = await func(*args, **kwargs)
        except TimeoutError:
            ret = RemoteServerError, None

        return ret

    return wrapper
