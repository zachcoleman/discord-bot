
_DEFAULT_BG_TIMER = 300

def background_register(registry: dict, sleep_time:int=None):
    if sleep_time is None:
        sleep_time = _DEFAULT_BG_TIMER
    
    def inner_func(func):
        registry[func.__name__] = {
            "method": func, 
            "sleep_time": sleep_time
        }
        return func
    
    return inner_func

def command_register(registry: dict, info=None):
    if info is None:
        info = "Bot command."    
    def inner_func(func):
        registry[func.__name__] = {
            "method": func,
            "info": info
        }
        return func
    
    return inner_func
