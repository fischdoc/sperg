""" the function registry thing. clients send configs of functions here ig """

rec_registry = {}


def register_rec(name, func=None):
    if func is not None:
        # register manually: register_rec("name", func)
        rec_registry[name] = func
        return func

    # register with decorator: @register_rec("name")
    def decorator(f):
        rec_registry[name] = f
        return f

    return decorator


'''
# old
def register_rec(name):
    def decorator(func):
        rec_registry[name] = func.__name__
        return func
    return decorator
'''
