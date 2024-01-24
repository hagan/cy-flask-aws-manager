import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Lambda stuff
    # BEARER_TOKEN = os.environ.get('BEARER_TOKEN', None)
    # APPSTREAM_API = os.environ.get('APPSTREAM_API', '/api/v1/appstream')
    # APPSTREAM_LAMBDA_ROOT_URL = os.environ.get('APPSTREAM_LAMBDA_ROOT_URL', 'http://localhost')
    # Local static files
    STATIC_ROOT = os.environ.get('STATIC_ROOT', '/tmp/static')
    # AppStream 2.0 Streaming URL hack
    # APPSTREAM_STREAMING_URL = os.environ.get('APPSTREAM_STREAMING_URL', None)
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
    #     or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

