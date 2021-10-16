from functools import wraps
from typing import Callable


def disable_for_loaddata(signal_handler: Callable):
    """Decorator that turns off signal handlers when loading fixture data."""

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw', False):
            return
        signal_handler(*args, **kwargs)

    return wrapper
