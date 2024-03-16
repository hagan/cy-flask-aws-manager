#awsmgr/app/blueprints/boto/services/dataclass.py

import os
import sys
import pprint
import dataclasses
from typing import ClassVar

from pymemcache.client.base import Client

DEBUG_THIS = False


AWSMGR_CONFIG_DATACLASS_DEFAULTS = {
    'AWS_DEFAULT_REGION': 'us-west-2',
    'AWS_SESSION_TOKEN_DURATION': 900
}

MEMCACHED_EXPIRE_DEFAULT = 1800
MEMCACHED_EXPIRE_DEFAULTS = {
    'AWS_ACCOUNT_ID': 0,
    'AWS_DEFAULT_REGION': 0,
    'AWS_CREDENTIAL_EXPIRATION': 0
}
pp = pprint.PrettyPrinter(indent=4)
debug_print = lambda *args, **kwargs: print(*args, **kwargs) if DEBUG_THIS is True else None

class AWSMgrConfigDataClassException(Exception):
    pass


def rewrite_sensitive_key(key, value):
    """
    If key is considered sensitive, change value for display
    """
    if not key or not value:
        return ''
    sensitive_keys = {
        'AWS_ACCESS_KEY_ID': 10,
        'AWS_SECRET_ACCESS_KEY': 15,
        'AWS_SESSION_TOKEN': 35
    }
    if((key.upper() in sensitive_keys.keys()) and (len(value) > 5)):
        ## MAX 35
        return value[0] + '*' * min((len(value) - 5), sensitive_keys.get(key.upper(), 10)) + value[-4:]
    return value


def memcached_check_available():
    debug_print("memcached_check_available()")
    client = Client(('localhost', 11212))
    try:
        client.set('awsmgr_test_key_is_running', True)
        value = client.get('awsmgr_test_key_is_running')
        client.close()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False
    return value


def memcached_get(key: str) -> int | str | dict:
    """
    Retrieves key from memcached
    """
    debug_print("memcached_get()")
    client = Client(('localhost', 11212))
    try:
        value = client.get(key)
        client.close()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return None
    return value


def memcached_set(key: str, value: int | str | dict, expire: int = 0) -> None:
    """
    Sets a value with a key in memcached
    """
    debug_print("memcached_get()")
    client = Client(('localhost', 11212))
    try:
        client.set(key, value, expire=expire)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
    client.close()


@dataclasses.dataclass
class AWSMgrConfigDataClass:
    aws_account_id: str = None
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_session_token: str = None
    aws_default_region: str = None
    aws_session_token_duration: int = None
    aws_credential_expiration: str = None
    aws_kms_key: str = None
    # Tracks when we import so we can update environment
    update_environ: ClassVar[list] = []
    update_memcached: ClassVar[list] = []

    def __init__(self, environment: dict = {}, skip_memcached: bool = False, *args, **kwargs):
        debug_print("AWSMgrConfigDataClass.__init__(env)")
        super().__init__(*args, **kwargs)
        for field in dataclasses.fields(self):
            debug_print(f'field: {field.name}')
        self.from_dict(environment)
        if not skip_memcached:
            self.from_memcached()
        self.from_environ()
        self.from_defaults()
        # verify aws credentials are good to good or blow up
        verify_is_not_empty = [
            'aws_account_id', 'aws_access_key_id', 'aws_secret_access_key',
            'aws_session_token', 'aws_default_region'
        ]
        empty_fields = []
        not_empty_fields = []
        for field in dataclasses.fields(self):
            if (field.name in verify_is_not_empty) and not getattr(self, field.name, None):
                empty_fields.append(field.name)
            else:
                not_empty_fields.append(field.name)
        if empty_fields:
            debug_print(f"Not empty fields: {', '.join(not_empty_fields)}")
            raise AWSMgrConfigDataClassException(f"AWSMgrConfigDataClass has empty field(s) {', '.join(empty_fields)} is/are empty")



        self.update_environment()


    def display(self):
        """
        """
        debug_print("AWSMgrConfigDataClass.display()")
        for field in dataclasses.fields(self):
            print(f"{field.name}: {getattr(self, field.name, '-x-')}")

    def from_dict(self, environment: dict, override: bool = False):
        """
        1st: Update variables from passed env dictionary (i.e. command line
        provided environment variable or was set manually)
        """
        debug_print("AWSMgrConfigDataClass.from_dict()")
        for env_var, val in environment.items():
            # User didn't pass value (--env VAR='blah' but --env VAR)
            # Pull VAR from environment.
            if val:
                self.update_environ.append(env_var)
                self.update_memcached.append(env_var)
            else:
                val = os.environ.get(env_var, None)
            # if we had a value for k/v, we use this for our dataclass!
            if(
                (val is not None) and
                hasattr(self, env_var.lower()) and
                ((getattr(self, env_var.lower(), None) is None) or override)
            ):
                debug_print(f"(1st) SETTING {env_var.lower()} -> {rewrite_sensitive_key(env_var, val)}")

                setattr(self, env_var.lower(), val)
            elif(not hasattr(self, env_var.lower())):
                raise AWSMgrConfigDataClassException(f"'{env_var.lower()}' does not exist in this dataclass!")

    def from_memcached(self, override: bool = False):
        """
        Updates all data dictionary vars from memcached (matching uppercase)
        """
        debug_print("AWSMgrConfigDataClass.update_from_memcached()")
        if memcached_check_available():
            debug_print("memcached is available")
            for field in dataclasses.fields(self):
                val = memcached_get(field.name.upper())
                val = val.decode('utf-8') if type(val) is bytes else val
                if val:
                    self.update_environ.append(field.name.upper())
                if(
                    (val is not None) and
                    ((getattr(self, field.name, None) is None) or override)
                ):
                    debug_print(f"(2nd) SETTING {field.name} -> {rewrite_sensitive_key(field.name, val)}")
                    setattr(self, field.name, val)

    def from_environ(self, override: bool = False):
        """
        Updates all dataclass fields with os.environ (matching uppercase)
        """
        debug_print("AWSMgrConfigDataClass.from_environ()")
        for field in dataclasses.fields(self):
            debug_print(f"AWSMgrConfigDataClass.from_environ() -- field: {field.name.upper()}")
            debug_print(pprint.pformat(os.environ))
            val = os.environ.get(field.name.upper(), '')
            debug_print(f"AWSMgrConfigDataClass.from_environ() -- value: {rewrite_sensitive_key(field.name, val)}")
            val = val.decode('utf-8') if type(val) is bytes else val
            if(
                (val is not None) and
                ((getattr(self, field.name, None) is None) or override)
            ):
                debug_print(f"(3rd) SETTING {field.name} -> {rewrite_sensitive_key(field.name, val)}")
                setattr(self, field.name, val)

    def from_defaults(self, override: bool = False):
        """
        Updates all dataclass fields with defaults
        """
        debug_print("AWSMgrConfigDataClass.update_from_defaults()")
        for field in dataclasses.fields(self):
            v = AWSMGR_CONFIG_DATACLASS_DEFAULTS.get(field.name, None)
            if(
                (v is not None) and
                ((getattr(self, field.name, None) is None) or override)
            ):
                debug_print(f"(4th) SETTING {field.name} -> {rewrite_sensitive_key(field.name, v)}")
                setattr(self, field.name, v)

    def update_environment(self):
        """
        Update our environ/memcached to current values to preserve
        """
        ## 1st - passed environment variables via --env take precidence and set environment and memcached
        for field in self.update_environ:
            val = getattr(self, field.lower(), None)
            if val:
                if( os.environ.get(field.upper(), '') != val ):
                    os.environ[field.upper()] = val
                    debug_print(f"(5th) Updating memcached {field} -> {rewrite_sensitive_key(field, val)}")
                if ( memcached_check_available() and ( memcached_get(field.upper()) != val ) ):
                    memcached_set(field.upper(), val, expire=MEMCACHED_EXPIRE_DEFAULTS.get(field.upper(), MEMCACHED_EXPIRE_DEFAULT))
        ## 2nd - pulled from memcached, set the environment
        for field in self.update_memcached:
            val = getattr(self, field.lower(), None)
            if ( val and (os.environ.get(field.upper(), '') != val) ):
                debug_print(f"(5th) Updating environment {field.upper()} -> {rewrite_sensitive_key(field, val)}")
                os.environ[field.upper()] = val


if __name__ == '__main__':
    acdc = AWSMgrConfigDataClass()
    acdc.display()