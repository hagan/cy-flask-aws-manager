import os
import pprint
from functools import wraps
from flask import current_app

## this wasn't working from the flask app init space
from pymemcache.client.base import Client

import shutil


class AWSConfigException(Exception):
    pass


def is_command_available(name):
    return shutil.which(name) is not None


def with_appcontext(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app = current_app._get_current_object()
        return f(app, *args, **kwargs)
    return decorated_function


def session_cred_dict(printf=print, **awsconfig):
    """
    Subset of credentials used to initialize an aws session
    """
    auth_keys = [
        'aws_access_key_id',
        'aws_secret_access_key',
        'aws_session_token'
    ]
    ret_dict = {key: awsconfig[key] for key in auth_keys if key in awsconfig }
    return ret_dict


def rewrite_sensitive_key(key, value):
    """
    If key is considered sensitive, change value for display
    """
    if (type(value) == bytes):
        value = value.decode("utf-8")
    sensitive_keys = [
        'AWS_SECRET_ACCESS_KEY',
        'AWS_SESSION_TOKEN'
    ]
    if((key.upper() in sensitive_keys) and (len(value) > 5)):
        ## MAX 35
        return value[0] + '*' * min((len(value) - 5), 35) + value[-4:]
    return value


def get_aws_config(skip_memcached=False, printf=print, env={}, **kwargs):
    """
    1) Use provided credentials
    2) Try memcached stored keys
    3) Use Config
    4) Config pulls from environment
    5) Use a default
    aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, tag_name, ec2_resource_name
    """
    #@TODO: move defaults to our flask config?
    awsdefaults = {
        'AWS_ACCESS_KEY_ID': None,
        'AWS_SECRET_ACCESS_KEY': None,
        'AWS_SESSION_TOKEN': None,
        'AWS_SESSION_TOKEN_DURATION': 900,
        'AWS_KMS_KEY': None,
        'AWS_DEFAULT_REGION': None,
        'AWS_PROFILE': None,
    }
    allowed_awsconfig = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_SESSION_TOKEN',
        'AWS_SESSION_TOKEN_DURATION',
        'AWS_KMS_KEY',
        'AWS_DEFAULT_REGION',
        'AWS_PROFILE',
    ]
    awsconfig = {}
    missed1 = []

    # printf("***************************")
    # printf(pprint.pformat(kwargs))
    # printf("***************************")

    # Store keys if passed kwargs have values set
    for i, (key, value) in enumerate(kwargs.items()):  # input keys are lowercase
        _key = key.upper()
        if ( ( value is not None ) and ( value != '' ) and ( _key in allowed_awsconfig ) ):
            printf(f"1st {i} passed value {_key} => {rewrite_sensitive_key(_key, value)}")
            awsconfig[_key] = value.decode('utf-8')
        elif ( ( value is not None ) and ( value == '' ) and ( _key in allowed_awsconfig ) ):
            # Use ENVIRONMENT
            if ( _key in env ):
                _val = env[_key].decode('utf-8')
                printf(f"1st passed environ {_key} => {rewrite_sensitive_key(_key, _val)}")
                awsconfig[_key] = _val
            else:
                missed1.append(_key)
        elif ( _key not in allowed_awsconfig ):
            raise AWSConfigException(f"{_key} is not a valid AWSConfig kwarg!")
        else:
            # value was None
            missed1.append(_key)

    # grab stored values from memcached
    missed2 = []
    try:
        pymemcache_client = Client(('localhost', 11212))
        memcached_keys = pymemcache_client.get_many(missed1)
    except Exception as e:
        if not skip_memcached:
            printf(f"Error: {e}")
        memcached_keys = {}
        missed2 = missed1
    else:
        for i, key in enumerate(missed1):
            if key in memcached_keys:
                value = memcached_keys[key]
                if (value is not None):
                    printf(f"2nd: {i} memcached {key} => {rewrite_sensitive_key(key, value)}")
                    awsconfig[key] = value.decode('utf-8')
                else:
                    missed2.append(key)
            else:
                missed2.append(key)

    missed3 = []
    # get from environment
    for i, key in enumerate(missed2):
        env_val = os.environ.get(key)
        if (env_val is not None):
            printf(f"3rd: {i} fetched environ {key} => {rewrite_sensitive_key(key, env_val)}")
            awsconfig[key] = env_val
        else:
            missed3.append(key)

    # get from default
    for i, key in enumerate(missed3):
        if key in awsdefaults:
            printf(f"4th: {i} default {key} => {rewrite_sensitive_key(key, awsdefaults[key])}")
            awsconfig[key] = awsdefaults[key]
        else:
            raise AWSConfigException(f"'{key}' had no default!")

    return {key.lower(): _ for key, _ in awsconfig.items()}
