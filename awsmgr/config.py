import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    VPC_NAME = os.environ.get('VPC_NAME', 'cyverse-example-vpc-name')
    # Pulumi configuration settings
    PULUMI_HOME = os.environ.get('PULUMI_HOME', '/home/cyverse/.pulumi')
    PULUMI_ORG_NAME = os.environ.get('PULUMI_ORG_NAME', '')
    PULUMI_PROJECT_NAME = os.environ.get('PULUMI_PROJECT_NAME', 'cyverse-awsmgr')
    PULUMI_STACK_NAME = os.environ.get('PULUMI_STACK_NAME', 'dev')
    PULUMI_PROJECT_DIR = os.environ.get('PULUMI_PROJECT_DIR', '/usr/local/var/pulumi')
    PULUMI_PROJECT_TEMPLATE = os.environ.get('PULUMI_PROJECT_TEMPLATE', '')
    # AWS settings

    ## @TODO: future maybe we pull data from this?
    # AWS_CONFIG_FILE = os.environ.get('AWS_CONFIG_FILE', None)
    ## Or use a profile?
    # AWS_PROFILE = os.environ.get('AWS_PROFILE', None)

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
    AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN', None)
    AWS_KMS_KEY = os.environ.get('AWS_KMS_KEY', None)
    # Not a valid aws environment var!
    AWS_SESSION_TOKEN_DURATION = os.environ.get('AWS_SESSION_TOKEN_DURATION', None)
    MEMCACHED_PORT = os.environ.get('MEMCACHED_PORT', 11212)

    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')

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
    BOTO3_SERVICES = ['s3', 'ec2']

