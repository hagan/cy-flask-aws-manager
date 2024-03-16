import os
from uuid import uuid4
from datetime import datetime
from time import time

from typing import Callable

from pymemcache.client.base import Client

import pytz
from boto3 import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


## Original: https://pritul95.github.io/blogs/boto3/2020/08/01/refreshable-boto3-session/
## updated ver here: https://stackoverflow.com/questions/63724485/how-to-refresh-the-boto3-credentials-when-python-script-is-running-indefinitely
## Credit to Ritul Patel & Xun Ren


TTL = 900  # default


class RefreshableBotoSession:
    """
    Boto Helper class which lets us create a refreshable session so that we can cache the client or resource.

    Usage
    -----
    session = RefreshableBotoSession().refreshable_session()

    client = session.client("s3") # we now can cache this client object without worrying about expiring credentials
    """

    def __init__(
        self,
        account_id: str = None,
        access_key_id: str = None,
        secret_access_key: str = None,
        session_token: str = None,
        region_name: str = None,
        profile_name: str = None,
        sts_arn: str = None,
        session_name: str = None,
        session_ttl: int = TTL,
        printf: Callable[[list, dict], None] = print
    ):
        """
        Initialize `RefreshableBotoSession`

        Parameters
        ----------
        access_key_id : str (optional)
            Empty, but use to prime session with access_id, secret_key & token auth

        secret_access_key : str (optional)
            Empty, but use to prime session with access_id, secret_key & token auth

        session_token : str (optional)
            Empty, but use to prime session with access_id, secret_key & token auth

        region_name : str (optional)
            Default region when creating a new connection.

        profile_name : str (optional)
            The name of a profile to use.

        sts_arn : str (optional)
            The role arn to sts before creating a session.

        session_name : str (optional)
            An identifier for the assumed role session. (required when `sts_arn` is given)

        session_ttl : int (optional)
            An integer number to set the TTL for each session. Beyond this session, it will renew the token.
            50 minutes by default which is before the default role expiration of 1 hour
        """
        self.print = printf
        self.print(f"RefreshableBotoSession::__init__(account_id={account_id}, access_key_id={access_key_id})")
        self.account_id = account_id
        self.access_key_id = access_key_id.decode("utf-8") if type(access_key_id) is bytes else access_key_id
        self.secret_access_key = secret_access_key.decode("utf-8") if type(secret_access_key) is bytes else secret_access_key
        self.session_token = session_token.decode("utf-8") if type(session_token) is bytes else session_token
        self.region_name = region_name.decode("utf-8") if type(region_name) is bytes else region_name
        self.profile_name = profile_name.decode("utf-8") if type(profile_name) is bytes else profile_name
        self.sts_arn = sts_arn
        self.session_name = session_name or uuid4().hex
        self.session_ttl = session_ttl

    def __get_session_credentials(self):
        """
        Get session credentials
        """
        self.print(f"self.access_key_id: {self.access_key_id}")
        session = Session(
            self.access_key_id,
            self.secret_access_key,
            self.session_token,
            region_name=self.region_name,
            profile_name=self.profile_name
        )
        # if(
        #     (self.access_key_id is not None) and
        #     (self.secret_access_key is not None) and
        #     (self.session_token is not None)
        # ):
        #     session = Session(
        #         self.access_key_id,
        #         self.secret_access_key,
        #         self.session_token,
        #         region_name=self.region_name
        #     )

        # if sts_arn is given, get credential by assuming the given role
        if self.sts_arn:
            self.print('OPTION A: sts_client = session.client(service_name="sts", region_name=self.region_name)')
            sts_client = session.client(service_name="sts", region_name=self.region_name)
            response = sts_client.assume_role(
                RoleArn=self.sts_arn,
                RoleSessionName=self.session_name,
                DurationSeconds=self.session_ttl,
            ).get("Credentials")

            ## Store new credentials
            access_key = response.get("AccessKeyId")
            self.print(f"**NEW** access_key: {access_key}, expires={self.session_ttl}")
            secret_key = response.get("SecretAccessKey")
            token = response.get("SessionToken")
            expiry_time = response.get("Expiration").isoformat()

            if access_key and secret_key and token and expiry_time:
                os.environ["AWS_ACCESS_KEY_ID"] = access_key
                os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
                os.environ["AWS_SESSION_TOKEN"] = token
                os.environ["AWS_CREDENTIAL_EXPIRATION"] = expiry_time
                try:
                    pymemcache_client = Client(('localhost', 11212))
                    pymemcache_client.set('AWS_ACCESS_KEY_ID', access_key, expire=self.session_ttl)
                    pymemcache_client.set('AWS_SECRET_ACCESS_KEY', secret_key, expire=self.session_ttl)
                    pymemcache_client.set('AWS_SESSION_TOKEN', token, expire=self.session_ttl)
                    pymemcache_client.set('AWS_CREDENTIAL_EXPIRATION', expiry_time, expire=self.session_ttl)
                except Exception:
                    pass
            credentials = {
                "access_key": access_key,
                "secret_key": secret_key,
                "token": token,
                "expiry_time": expiry_time,
            }
        else:
            self.print("OPTION B: session_credentials = session.get_credentials().get_frozen_credentials()")
            session_credentials = session.get_credentials().get_frozen_credentials()
            credentials = {
                "access_key": session_credentials.access_key,
                "secret_key": session_credentials.secret_key,
                "token": session_credentials.token,
                "expiry_time": datetime.fromtimestamp(time() + self.session_ttl).replace(tzinfo=pytz.utc).isoformat(),
            }

        return credentials

    def refreshable_session(self) -> Session:
        """
        Get refreshable boto3 session.
        """
        # Get refreshable credentials
        self.print("refreshable_session()")
        refreshable_credentials = RefreshableCredentials.create_from_metadata(
            metadata=self.__get_session_credentials(),
            refresh_using=self.__get_session_credentials,
            method="sts-assume-role",
        )

        # attach refreshable credentials current session
        session = get_session()
        session._credentials = refreshable_credentials
        session.set_config_variable("region", self.region_name)
        autorefresh_session = Session(botocore_session=session)

        return autorefresh_session
