from typing import Callable, Dict

_DEFAULT_BG_TIMER = 300


def background_register(
    registry: Dict[str, Callable], daily_time: int = None, sleep_time: int = None
):
    if sleep_time is None:
        sleep_time = _DEFAULT_BG_TIMER

    def inner_func(func):
        registry[func.__name__] = {
            "method": func,
            "sleep_time": sleep_time,
            "daily_time": daily_time,
        }
        return func

    return inner_func


def command_register(registry: Dict[str, Callable], info: str = None):
    if info is None:
        info = "Bot command."

    def inner_func(func):
        registry[func.__name__] = {"method": func, "info": info}
        return func

    return inner_func


def random_register(registry: Dict[str, Callable], prob: float = None):
    assert prob <= 1 and prob >= 0, "prob must be in [0, 1]."

    def inner_func(func):
        registry[func.__name__] = {"method": func, "prob": prob}
        return func

    return inner_func
