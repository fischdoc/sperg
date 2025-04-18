""" the function registry thing. clients send configs of functions here ig """

rec_registry = {}

'''
def register_rec(name):
    def decorator(func):
        rec_registry[name] = func.__name__
        return func
    return decorator'''


def register_rec(name, func=None):
    if func:
        rec_registry[name] = func

    def decorator(f):
        rec_registry[name] = f
        return f
    return decorator if func is None else None
