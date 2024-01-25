# -*- encoding: utf-8 -*-
"""

"""
import os
import logging

# from werkzeug.middleware.proxy_fix import ProxyFix
# from flask_app import app_name
# from awsmgr import app as app_module
from awsmgr.app import create_app
# generic config
from awsmgr.config import Config as ConfigClass
# from flask_app.app import create_app, db


# gunicorn_logger = logging.getLogger('gunicorn.error')


app = create_app(
    config_class=ConfigClass
    # app_name=app_name
    # logger_override=gunicorn_logger
)

# print(f"(wsgi) PUBLIC_KEY: {app.config['PUBLIC_KEY']}")

# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)