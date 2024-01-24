import pprint

from flask import Flask

from flask_static_digest import FlaskStaticDigest
from flask_cors import CORS

from flask.awsmgr.config import Config


pp = pprint.PrettyPrinter(indent=4)
flask_static_digest = FlaskStaticDigest()
cors = CORS() # resources={r"/api/*": {"origins": "*"}}


def configure_cli(app):
    """Configure Flask 2.0's cli for easy entity management"""
    from . import commands
    for cmd in commands.__commands__:
        app.cli.add_command(cmd)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize Flask extensions here

     # Register blueprints here
    from awsmgr.app.main import bp as main_bp
    app.register_blueprint(main_bp)

    flask_static_digest.init_app(app)
    cors.init_app(app, resources={r"/Staging/awsmgr/*": {"origins": "*"}})

    configure_cli(app)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app