from functools import wraps
from flask import current_app

import shutil


def is_command_available(name):
    return shutil.which(name) is not None


def with_appcontext(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app = current_app._get_current_object()
        return f(app, *args, **kwargs)
    return decorated_function