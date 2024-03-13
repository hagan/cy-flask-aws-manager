# -*- coding: utf-8 -*-
"""Click commands."""

import sys
import os
import pprint
import click
import boto3

# from flask import Flask

from awsmgr.app import create_app
from awsmgr.app.blueprints.pulumi.services import pulumi_setup_stack_call
from awsmgr.app.blueprints.pulumi.services.s3bucket import pulumi_s3_bucket_func
from awsmgr.app.blueprints.pulumi.services.ec2instance import pulumi_ec2_instance_func
# from awsmgr.app.blueprints.pulumi.commands import base_awscmd

from awsmgr.app.utils import get_aws_config, session_cred_dict, AWSConfigException
from awsmgr.app.blueprints.boto.services import boto3_get_session, boto3_start_ec2, boto3_stop_ec2, boto3_renew_token, boto3_get_caller_id, BotoException

# from awsmgr.config import Config

DEFAULT_TAG_NAME = 'Demo Cyverse'

DEFAULT_S3_BUCKET_NAME = 'my-awsmgr-s3-bucket'

DEFAULT_RESOURCE_NAME = 'my-awsmgr-ec2-server'
DEFAULT_INSTANCE_TYPE = 't2.micro'
DEFAULT_AMI = 'ami-0895022f3dac85884'


def process_env(ctx, param, value):
    env_vars = {}
    if value:
        for item in value:
            parts = item.split('=', 1)
            if len(parts) == 2:
                env_vars[parts[0]] = parts[1]
            else:
                env_vars[parts[0]] = os.environ.get(parts[0], None)
    return env_vars


@click.group()
def main():
    """AWSMGR command: create/destroy/start/stop ec2 instance"""


@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--bucket-name', default=DEFAULT_S3_BUCKET_NAME, help="AWS_DEFAULT_PROFILE environment variable override")
def create_s3(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, bucket_name):
    f"""
    Provisioning '{bucket_name}' s3 bucket.
    """
    click.echo(f"\t[1] Provisioning '{bucket_name}' S3 bucket")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']
        aws_region = app.config['AWS_REGION']

        pulumi_setup_stack_call(
            lambda: pulumi_s3_bucket_func(bucket_name),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            aws_region,
            setup=True,
            printf=click.echo
        )

@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--bucket-name', default=DEFAULT_S3_BUCKET_NAME, help="S3 Bucket name")
def destroy_s3(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, bucket_name):
    f"""
    Deprovisioning '{bucket_name}' s3 bucket.
    """
    click.echo(f"\t[1] Destroying '{bucket_name}' S3 bucket")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']
        aws_region = app.config['AWS_REGION']

        pulumi_setup_stack_call(
            lambda: pulumi_s3_bucket_func(bucket_name),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            aws_region,
            setup=False,
            printf=click.echo
        )

@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
@click.option('--instance-type', default=DEFAULT_INSTANCE_TYPE, help=f"Instance type, ie {DEFAULT_INSTANCE_TYPE}")
@click.option('--ami', default=DEFAULT_AMI, help=f"AMI, ie {DEFAULT_AMI}")
def create_ec2(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, tag_name, ec2_resource_name, instance_type, ami):
    f"""
    Create an EC2 instance.
    """
    click.echo(f"\t[1] Provisioning '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']
        aws_region = app.config['AWS_REGION']

        pulumi_setup_stack_call(
            lambda: pulumi_ec2_instance_func(ec2_resource_name, instance_type, ami, tags={'Name': tag_name}),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            aws_region,
            setup=True,
            printf=click.echo
        )

@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
@click.option('--instance-type', default=DEFAULT_INSTANCE_TYPE, help=f"Instance type, ie {DEFAULT_INSTANCE_TYPE}")
@click.option('--ami', default=DEFAULT_AMI, help=f"AMI, ie {DEFAULT_AMI}")
def destroy_ec2(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, tag_name, ec2_resource_name, instance_type, ami):
    f"""
    Destroy an EC2 instance.
    """
    click.echo(f"\t[1] Deprovisioning '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']
        aws_region = app.config['AWS_REGION']

        pulumi_setup_stack_call(
            lambda: pulumi_ec2_instance_func(ec2_resource_name, instance_type, ami, tags={'Name': tag_name}),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            aws_region,
            setup=False,
            printf=click.echo
        )


@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
def start_ec2(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, tag_name, ec2_resource_name):
    f"""
    Start an EC2 instance.
    """
    click.echo(f"\t[1] Starting '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        aws_region = app.config['AWS_REGION']
        boto3_start_ec2(ec2_resource_name, printf=click.echo)


@main.command()
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY environment variable override")
@click.option('--aws-access-key-id', default=None, help="AWS_ACCESS_KEY_ID environment variable override")
@click.option('--aws-secret-access-key', default=None, help="AWS_SECRET_ACCESS_KEY environment variable override")
@click.option('--aws-region', default=None, help="AWS_DEFAULT_REGION environment variable override")
@click.option('--aws-profile', default=None, help="AWS_DEFAULT_PROFILE environment variable override")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
def stop_ec2(aws_kms_key, aws_access_key_id, aws_secret_access_key, aws_region, aws_profile, tag_name, ec2_resource_name):
    f"""
    Stop an EC2 instance.
    """
    click.echo(f"\t[1] Stopping '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        aws_region = app.config['AWS_REGION']
        boto3_stop_ec2(ec2_resource_name, printf=click.echo)


@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-f', '--fakeit', is_flag=True, show_default=True, default=False, help="Fake the generate of session tokens, used to check we have aws permission")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--aws-session-token-duration', required=False, default=None, type=int, help="AWS_SESSION_TOKEN_DURATION")
def renew_token(env: dict, fakeit: bool, skip_memcached: bool, aws_session_token_duration: int):
    f"""
    Renew the temporary token
    """
    click.echo("\t[1] Initialize Flask application stack")

    app = create_app()
    with app.app_context():
        ## Get current config state
        click.echo(f"\t[2] Gathering credentials")
        awsconfig = get_aws_config(
            skip_memcached=skip_memcached,
            printf=click.echo,
            env=env,
            **{
                'aws_access_key_id': None,
                'aws_secret_access_key': None,
                'aws_session_token': None,
                'aws_session_token_duration': aws_session_token_duration,
            }
        )

        # click.echo(pprint.pformat(session_cred_dict(**awsconfig)))
        #
        # session = boto3.Session(**credentials)
        session = boto3_get_session(
            printf=click.echo,
            awsconfig=session_cred_dict(printf=click.echo, **awsconfig)
        )

        # click.echo(f"\t[2b] Got credentials")
        # if not fakeit:
        #     click.echo(f"\t[3] Renewing temporary token")
        #     try:
        #         res = boto3_renew_token(
        #             printf=click.echo,
        #             session=session  # keys are provided in uppercase!
        #         )
        #     except BotoException as e:
        #         if e.status == 2:
        #             click.echo("Token expired", err=True)
        #         else:
        #             click.echo(e.message, err=True)
        #         sys.exit(1)
        #     else:
        #         sys.exit(0)
        # else:
        #     click.echo(f"\t[3] Testing credentials")
        #     try:
        #         caller_id = boto3_get_caller_id(
        #             printf=click.echo,
        #             session=session
        #         )
        #     except BotoException as e:
        #         if e.status == 2:
        #             click.echo("Token expired", err=True)
        #         else:
        #             click.echo(e.message, err=True)
        #         sys.exit(1)
        #     else:
        #         click.echo(f"Caller credentials {caller_id}")
        #         sys.exit(0)

if __name__ == "__main__":
    main()
