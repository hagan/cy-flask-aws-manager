import pprint

from flask import Flask

from flask_static_digest import FlaskStaticDigest
from flask_cors import CORS

from awsmgr.config import Config


pp = pprint.PrettyPrinter(indent=4)
flask_static_digest = FlaskStaticDigest()
cors = CORS() # resources={r"/api/*": {"origins": "*"}}


def configure_cli(app, cli):
    """Configure Flask 2.0's cli for easy entity management"""
    # from . import commands
    for cmd in cli.__commands__:
        app.cli.add_command(cmd)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize Flask extensions here

     # Register blueprints here
    from awsmgr.app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from awsmgr.app.blueprints.ec2 import bp as ec2_bp
    app.register_blueprint(ec2_bp)

    from awsmgr.app.blueprints.lambdas import bp as lambdas_bp
    app.register_blueprint(lambdas_bp)

    from awsmgr.app.blueprints.pulumi import bp as vpc_bp
    app.register_blueprint(vpc_bp)

    flask_static_digest.init_app(app)
    cors.init_app(app, resources={r"/Staging/awsmgr/*": {"origins": "*"}})

    # Register blueprints commands here
    from . import commands
    configure_cli(app, commands)

    from awsmgr.app.blueprints.ec2 import commands as ec2_cli
    configure_cli(app, ec2_cli)

    from awsmgr.app.blueprints.lambdas import commands as lambdas_cli
    configure_cli(app, lambdas_cli)

    from awsmgr.app.blueprints.main import commands as main_cli
    configure_cli(app, main_cli)

    from awsmgr.app.blueprints.pulumi import commands as pulumi_cli
    configure_cli(app, pulumi_cli)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app