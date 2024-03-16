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


# from awsmgr.app.utils import get_aws_config, session_cred_dict, AWSConfigException
from awsmgr.app.blueprints.boto.services import boto3_get_session, boto3_start_ec2, boto3_stop_ec2, boto3_renew_token, boto3_get_caller_id, BotoException
from awsmgr.app.blueprints.boto.services.dataclass import AWSMgrConfigDataClass

# from awsmgr.config import Config

DEFAULT_TAG_NAME = 'Demo Cyverse'

DEFAULT_S3_BUCKET_NAME = 'cy-awsmgr-bucket-2024'

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
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--bucket-name', default=DEFAULT_S3_BUCKET_NAME, help="AWS_DEFAULT_PROFILE environment variable override")
def create_s3(env: dict, skip_memcached: bool, bucket_name: str):
    f"""
    Provisioning '{bucket_name}' s3 bucket.
    """
    click.echo(f"\t[1] Provisioning '{bucket_name}' S3 bucket")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)

        ## @TODO Move these Project name/stackname/dir into our dataclass?
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']

        pulumi_setup_stack_call(
            lambda: pulumi_s3_bucket_func(bucket_name),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            acdc.aws_default_region,
            setup=True,
            printf=click.echo
        )

@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--bucket-name', default=DEFAULT_S3_BUCKET_NAME, help="S3 Bucket name")
def destroy_s3(env: dict, skip_memcached: bool, bucket_name: str):
    f"""
    Deprovisioning '{bucket_name}' s3 bucket.
    """
    click.echo(f"\t[1] Destroying '{bucket_name}' S3 bucket")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        ## @TODO This isn't being used?.. needs to override os environment I think
        awsconfig = get_aws_config(
            skip_memcached=skip_memcached,
            printf=click.echo,
            env=env,
            **{
                'aws_account_id': None,
                'aws_access_key_id': None,
                'aws_secret_access_key': None,
                'aws_session_token': None,
                'aws_default_region': None,
                'aws_credential_expiration': None,
                # 'aws_session_token_duration': 900,
            }
        )
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']

        pulumi_setup_stack_call(
            lambda: pulumi_s3_bucket_func(bucket_name),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            awsconfig['aws_default_region'],
            setup=False,
            printf=click.echo
        )


@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
@click.option('--instance-type', default=DEFAULT_INSTANCE_TYPE, help=f"Instance type, ie {DEFAULT_INSTANCE_TYPE}")
@click.option('--ami', default=DEFAULT_AMI, help=f"AMI, ie {DEFAULT_AMI}")
def create_ec2(env: dict, skip_memcached: bool, tag_name: str, ec2_resource_name: str, instance_type: str, ami: str) -> None:
    f"""
    Create an EC2 instance.
    """
    click.echo(f"\t[1] Provisioning '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']

        pulumi_setup_stack_call(
            acdc,
            lambda: pulumi_ec2_instance_func(acdc, ec2_resource_name, instance_type, ami, tags={'Name': tag_name}),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            setup=True,
            printf=click.echo
        )

@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
@click.option('--instance-type', default=DEFAULT_INSTANCE_TYPE, help=f"Instance type, ie {DEFAULT_INSTANCE_TYPE}")
@click.option('--ami', default=DEFAULT_AMI, help=f"AMI, ie {DEFAULT_AMI}")
def destroy_ec2(env: dict, skip_memcached: bool, tag_name: str, ec2_resource_name: str, instance_type: str, ami: str) -> None:
    f"""
    Destroy an EC2 instance.
    """
    click.echo(f"\t[1] Deprovisioning '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        click.echo("\t[3] Initialized app context")
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)
        project_name = app.config['PULUMI_PROJECT_NAME']
        stack_name = app.config['PULUMI_STACK_NAME']
        pulumi_project_dir = app.config['PULUMI_PROJECT_DIR']
        pulumi_home_dir = app.config['PULUMI_HOME']
        pulumi_setup_stack_call(
            acdc,
            lambda: pulumi_ec2_instance_func(acdc, ec2_resource_name, instance_type, ami, tags={'Name': tag_name}),
            project_name,
            stack_name,
            pulumi_project_dir,
            pulumi_home_dir,
            setup=False,
            printf=click.echo
        )


@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
def start_ec2(env: dict, skip_memcached: bool, tag_name: bool, ec2_resource_name: str):
    f"""
    Start an EC2 instance.
    """
    click.echo(f"\t[1] Starting '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)
        boto3_start_ec2(acdc, ec2_resource_name, printf=click.echo)


@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
@click.option('--tag-name', default=DEFAULT_TAG_NAME, help="DEFAULT_TAG_NAME environment variable override")
@click.option('--ec2-resource-name', default=DEFAULT_RESOURCE_NAME, help=f"EC2 resource name, ie {DEFAULT_RESOURCE_NAME}")
def stop_ec2(env: dict, skip_memcached: bool, tag_name: str, ec2_resource_name: str):
    f"""
    Stop an EC2 instance.
    """
    click.echo(f"\t[1] Stopping '{ec2_resource_name}' EC2 resource")
    click.echo("\t[2] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)
        boto3_stop_ec2(acdc, ec2_resource_name, printf=click.echo)


@main.command()
@click.option('-e', '--env', multiple=True, callback=process_env, help="Set/use an environment var by --env VAR_NAME='value' or --env VAR_NAME to use matching environment variable")
@click.option('-f', '--fakeit', is_flag=True, show_default=True, default=False, help="Fake the generate of session tokens, used to check we have aws permission")
@click.option('-m', '--skip-memcached', is_flag=True, show_default=True, default=False, help="Don't poll memcached for variable")
def renew_token(env: dict, fakeit: bool, skip_memcached: bool):
    f"""
    Renew the temporary token
    """
    click.echo("\t[1] Initialize Flask application stack")
    app = create_app()
    with app.app_context():
        ## Get current config state
        click.echo(f"\t[2] Gathering credentials")
        acdc = AWSMgrConfigDataClass(environment=env, skip_memcached=skip_memcached)
        if not fakeit:
            click.echo("NOT FAKING")
            session = boto3_get_session(acdc)
        else:
            # @TODO: please implement this.. autorefresh token might not need it anymore
            raise Exception("Not yet implemented")

if __name__ == "__main__":
    main()
