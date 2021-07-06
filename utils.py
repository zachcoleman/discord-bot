
import requests

async def url_request(url):
    resp = requests.get(url)
    return resp

def background_register(registry: dict, sleep_time:int=None):
    def inner_func(self, func):
        if sleep_time is None:
            sleep_time = _DEFAULT_BG_TIMER
        registry[func.__name__] = (func, sleep_time)
        return func
    return inner_func
