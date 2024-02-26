import click
import sys
import asyncio

# from flask import current_app
# from flask.cli import with_appcontext

from . import services as pulumi_services
from .services import create_dir, pulumi_main_stack

# @with_appcontext
def base_awscmd(
    command,
    aws_kms_key=None,
    project_name=None,
    stack_name=None,
    pulumi_project_dir=None,
    pulumi_home_dir=None,
    aws_region=None
):
    ## Test if we have aws kms key or the user/token keys..
    # @TODO: add AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
    if (not aws_kms_key):
        click.echo("Must provide AWS_KMS_KEY via an Environment variable or by passing in command line!")
        sys.exit(1)

    valid_cmds = {
        'create-s3', 'destroy-s3', 'create-vpc', 'destroy-vpc'
    }
    if command not in valid_cmds:
        click.echo(f"'{command}' was not a valid command, try one of: {','.join(valid_cmds)}")

    # @TODO make sure our directory exists/mounted/created
    create_dir(pulumi_project_dir)
    pulumi_main_stack(
        command,
        aws_kms_key=aws_kms_key,
        project_name=project_name,
        stack_name=stack_name,
        pulumi_project_dir=pulumi_project_dir,
        pulumi_home_dir=pulumi_home_dir,
        aws_region=aws_region,
        printf=click.echo
    )



__commands__ = [
    # awscmd,
]