# -*- encoding: utf-8 -*-
"""

"""
import os
import logging

# from werkzeug.middleware.proxy_fix import ProxyFix
# from flask_app import app_name
# from appstreamer import app as app_module
from awsmgr.app import create_app
# generic config
from flask.awsmgr.config import Config as ConfigClass
# from flask_app.app import create_app, db


# gunicorn_logger = logging.getLogger('gunicorn.error')


app = create_app(
    config_class=ConfigClass
    # app_name=app_name
    # logger_override=gunicorn_logger
)
# print(f"(wsgi) BEARER_TOKEN: {app.config['BEARER_TOKEN']}")
# print(f"(wsgi) APPSTREAM_API: {app.config['APPSTREAM_API']}")
# print(f"(wsgi) APPSTREAM_LAMBDA_ROOT_URL: {app.config['APPSTREAM_LAMBDA_ROOT_URL']}")
# print(f"(wsgi) APPSTREAM_STREAMING_URL: {app.config['APPSTREAM_STREAMING_URL']}")
# print(f"(wsgi) PUBLIC_KEY: {app.config['PUBLIC_KEY']}")

# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)