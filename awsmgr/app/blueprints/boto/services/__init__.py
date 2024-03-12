import boto3
import pprint
import sys
import re

from botocore.exceptions import NoCredentialsError, ClientError
from boto3.session import Session

from awsmgr.app.utils import session_cred_dict

from flask import current_app


class BotoException(Exception):
    def __init__(self, message, status=0, code=''):
        super().__init__(message)
        self.status = status
        self.code = code


def find_instance_id_by_name(resource_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [resource_name]
            }
        ]
    )
    for reservation in response['Reservations']:
        for instance in reservation['Instance']:
            return instance['InstanceId']
    return None


def boto3_start_ec2(ec2_resource_name, printf=print):
    printf(f"boto3_start_ec2({ec2_resource_name})")
    ec2 = boto3.resource('ec2')

    instance_id = find_instance_id_by_name(ec2_resource_name)
    if instance_id:
        instance = ec2.Instance(instance_id)
        printf("Starting instance: {instance_id}")
        response = instance.start()
        printf(response)
    else:
        printf(f"ERROR: Could not find {ec2_resource_name}")


def boto3_stop_ec2(ec2_resource_name, printf=print):
    printf(f"boto3_stop_ec2({ec2_resource_name})")
    ec2 = boto3.resource('ec2')
    instance_id = find_instance_id_by_name(ec2_resource_name)
    if instance_id:
        instance = ec2.Instance(instance_id)
        printf("Stopping instance: {instance_id}")
        response = instance.stop()
        printf(response)
    else:
        printf(f"ERROR: Could not find {ec2_resource_name}")


def boto3_get_caller_id(printf=print, session: Session=None, awsconfig: dict ={}):
    """
    Get our user's id (used for testing credentials work)

    res looks like: {
        'UserId': 'AR***************7J4Y:AwsManagerRoleSession',
        'Account': '12********56',
        'Arn': 'arn:aws:sts::12********56:assumed-role/AWSManagerRole/AwsManagerRoleSession',
        'ResponseMetadata': {
            'RequestId': '########-####-####-####-############',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'x-amzn-requestid': '########-####-####-####-############',
                'content-type': 'text/xml',
                'content-length': '463',
                'date': 'Mon, 01 Jan 2020 00:00:00 GMT'
            },
            'RetryAttempts': 0
        }
    }
    """
    if((session is None) and awsconfig):
        session = boto3.Session(**session_cred_dict(**awsconfig))
    elif(session is None and not awsconfig):
        raise BotoException("ERROR: Requires a Session object or awsconfig dictionary!", status=1, code='PEBCAK')

    printf("Testing with session?")
    sts_client = session.client('sts')
    try:
        res = sts_client.get_caller_identity()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ExpiredToken':
            raise BotoException("Error: Expired Token", status=2, code='ExpiredToken')
        else:
            raise e
    else:
        account_id = res['Account'] if 'Account' in res else None
        printf(pprint.pformat(res))
        user_id, role_id = None, None
        if('UserId' in res):
            match = re.match(r'^([^:]+)', res['UserId'])
            if match:
                user_id = match.group(0)
            match = re.match(r'^(?:[^:]+)(?::([^:]*))?$', res['UserId'])
            if match:
                role_id = match.group(1)
        printf(f"account_id: {account_id} user_id: {user_id} role_id: {role_id}")
        return account_id, user_id, role_id


def boto3_renew_token(role_session_name: str="AWSManagerRole", printf=print, session: Session=None, awsconfig: dict={}):
    """
    using assume_role to regenerate a new token
    """
    if session is None:
        raise Exception("ERROR: must pass a valid boto3 Session object!")
    sts_client = session.client('sts')
    account_id, user_id, role_id = boto3_get_caller_id(printf=printf, session=session)
    if user_id is None:
        raise BotoException("Error: Failed to aquire UserId", status=3, code='NoUserId')
    else:
        printf(f"user_id: {user_id}")
    printf(f"boto3_renew_token()")
    try:
        duration = awsconfig['AWS_SESSION_TOKEN_DURATION'] if 'AWS_SESSION_TOKEN_DURATION' in awsconfig else 900
        printf(f"~~~~~~~~~~~~~~  sts_client.assume_role : {duration}  ~~~~~~~~~~~~~~")
        response = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/{role_session_name}",
            RoleSessionName=role_session_name,
            DurationSeconds=duration
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ExpiredToken':
            raise BotoException("Error: Expired Token", status=2, code='ExpiredToken')
        else:
            raise e
    else:
        printf(pprint.pformat(response))

    access_key_id = None
    secret_access_key = None
    session_token = None
    expiration = None
    errored = False

    if response and 'Credentials' in response:
        credentials = response['Credentials']
        if credentials and 'AccessKeyId' in credentials:
            access_key_id = credentials['AccessKeyId']
        if credentials and 'SecretAccessKey' in credentials:
            secret_access_key = credentials['SecretAccessKey']
        if credentials and 'SessionToken' in credentials:
            session_token = credentials['SessionToken']
        if credentials and 'Expiration' in credentials:
            expiration = credentials['Expiration']

    if access_key_id is not None:
        _access_key_id = current_app.memcached_client.get('AWS_ACCESS_KEY_ID')
        printf(f"before aws_access_key_id = {_access_key_id}")
        try:
            current_app.memcached_client.set('AWS_ACCESS_KEY_ID', access_key_id, expire=duration+60)
        except ConnectionRefusedError:
            return None
        _access_key_id = current_app.memcached_client.get('AWS_ACCESS_KEY_ID')
        printf(f"after aws_access_key_id = {_access_key_id}")
    else:
        printf(f"ERROR: No AccessKeyId found!")
        errored = True

    if secret_access_key is not None:
        _secret_access_key = current_app.memcached_client.get('AWS_SECRET_ACCESS_KEY')
        printf(f"before secret_access_key = {_secret_access_key}")
        current_app.memcached_client.set('AWS_SECRET_ACCESS_KEY', secret_access_key, expire=duration+60)
        _secret_access_key = current_app.memcached_client.get('AWS_SECRET_ACCESS_KEY')
        printf(f"after secret_access_key = {_secret_access_key}")
    else:
        printf(f"ERROR: No SecretAccessKey found!")
        errored = True

    if session_token is not None:
        _session_token = current_app.memcached_client.get('AWS_SESSION_TOKEN')
        printf(f"before session_token = {_session_token}")
        current_app.memcached_client.set('AWS_SESSION_TOKEN', session_token, expire=duration+60)
        _session_token = current_app.memcached_client.get('AWS_SESSION_TOKEN')
        printf(f"after expiration = {_session_token}")
    else:
        printf(f"ERROR: No SessionToken found!")
        errored = True

    if expiration is not None:
        _expiration = current_app.memcached_client.get('AWS_EXPIRATION')
        printf(f"before session_token = {_expiration}")
        current_app.memcached_client.set('AWS_EXPIRATION', expiration, expire=duration+60)
        _expiration = current_app.memcached_client.get('AWS_EXPIRATION')
        printf(f"after expiration = {_expiration}")
    else:
        printf(f"ERROR: No Expiration found!")
        errored = True

    if not errored:
        return {
            'access_key_id': access_key_id,
            'secret_access_key': secret_access_key,
            'session_token': session_token,
            'expiration': expiration
        }
    else:
        return {}