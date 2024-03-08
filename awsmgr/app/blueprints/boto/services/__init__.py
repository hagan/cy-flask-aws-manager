import boto3
import pprint
import sys

from botocore.exceptions import NoCredentialsError

from flask import current_app


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


def boto3_renew_token(role_session_name="AWSManagerRole", duration=900, printf=print):
    """
    using assume_role to regenerate a new token
    """
    printf(f"boto3_renew_token()")
    sts_client = boto3.client('sts')
    try:
        caller_identity = sts_client.get_caller_identity()
    except NoCredentialsError:
        printf("ERROR: Unable to locate credentials")
        sys.exit(1)

    try:
        response = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{caller_identity}:role/{role_session_name}",
            RoleSessionName=role_session_name,
            DurationSeconds=duration
        )
    except NoCredentialsError:
        printf("ERROR: Unable to locate credentials")
        sys.exit(1)

    access_key_id = None
    secret_access_key = None
    session_token = None
    expiration = None

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
        current_app.memcached_client.set('AWS_ACCESS_KEY_ID', access_key_id, expire=duration+60)
        _access_key_id = current_app.memcached_client.get('AWS_ACCESS_KEY_ID')
        printf(f"after aws_access_key_id = {_access_key_id}")
    if secret_access_key is not None:
        _secret_access_key = current_app.memcached_client.get('AWS_SECRET_ACCESS_KEY')
        printf(f"before secret_access_key = {_secret_access_key}")
        current_app.memcached_client.set('AWS_SECRET_ACCESS_KEY', secret_access_key, expire=duration+60)
        _secret_access_key = current_app.memcached_client.get('AWS_SECRET_ACCESS_KEY')
        printf(f"after secret_access_key = {_secret_access_key}")
    if session_token is not None:
        _session_token = current_app.memcached_client.get('AWS_SESSION_TOKEN')
        printf(f"before session_token = {_session_token}")
        current_app.memcached_client.set('AWS_SESSION_TOKEN', session_token, expire=duration+60)
        _session_token = current_app.memcached_client.get('AWS_SESSION_TOKEN')
        printf(f"after expiration = {_session_token}")
    if expiration is not None:
        _expiration = current_app.memcached_client.get('AWS_EXPIRATION')
        printf(f"before session_token = {_expiration}")
        current_app.memcached_client.set('AWS_EXPIRATION', expiration, expire=duration+60)
        _expiration = current_app.memcached_client.get('AWS_EXPIRATION')
        printf(f"after expiration = {_expiration}")
