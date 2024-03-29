# awsmgr/flask_boto3/__init__.py
# This code was originally sourced from flask_boto3 -> https://github.com/Ketouem/flask-boto3/

import boto3
from botocore.exceptions import UnknownServiceError

from flask import current_app, g
import click

class Boto3:
    """Stores a bunch of boto3 conectors inside Flask's application context
    for easier handling inside view functions.

    All connectors are stored inside the dict `boto3_cns` where the keys are
    the name of the services and the values their associated boto3 client.
    """
    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Register our teardown?
        """
        @app.teardown_appcontext
        def teardown(exception=None):
            """This is called when app context is closed"""
            if hasattr(g, 'boto3_cns'):
                for c in g.boto3_cns:
                    con = g.boto3_cns[c]
                    if hasattr(con, 'close') and callable(con.close):
                        con.close()

    def connect(self):
        """Iterate through the application configuration and instantiate
        the services.
        """
        requested_services = set(
            svc.lower() for svc in current_app.config.get('BOTO3_SERVICES', [])
        )

        region = current_app.config.get('AWS_REGION')
        sess_params = {
            'aws_access_key_id': current_app.config.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': current_app.config.get('AWS_SECRET_ACCESS_KEY'),
            'profile_name': current_app.config.get('AWS_PROFILE'),
            'region_name': region
        }
        sess = boto3.session.Session(**sess_params)

        try:
            cns = {}
            for svc in requested_services:
                # Check for optional parameters
                params = current_app.config.get(
                    'BOTO3_OPTIONAL_PARAMS', {}
                ).get(svc, {})

                # Get session params and override them with kwargs
                # `profile_name` cannot be passed to clients and resources
                kwargs = sess_params.copy()
                kwargs.update(params.get('kwargs', {}))
                del kwargs['profile_name']

                # Override the region if one is defined as an argument
                args = params.get('args', [])
                if len(args) >= 1:
                    del kwargs['region_name']

                if not(isinstance(args, list) or isinstance(args, tuple)):
                    args = [args]

                # Create resource or client
                if svc in sess.get_available_resources():
                    cns.update({svc: sess.resource(svc, *args, **kwargs)})
                else:
                    cns.update({svc: sess.client(svc, *args, **kwargs)})
        except UnknownServiceError:
            raise
        return cns

    @property
    def resources(self):
        c = self.connections
        return {k: v for k, v in c.items() if hasattr(c[k].meta, 'client')}

    @property
    def clients(self):
        """
        Get all clients (with and without associated resources)
        """
        clients = {}
        for k, v in self.connections.items():
            if hasattr(v.meta, 'client'):       # has boto3 resource
                clients[k] = v.meta.client
            else:                               # no boto3 resource
                clients[k] = v
        return clients

    @property
    def connections(self):
        if not hasattr(g, 'boto3_cns'):
            g.boto3_cns = self.connect()
        return g.boto3_cns
