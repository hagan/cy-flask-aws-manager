import click
import sys
import asyncio

from flask import current_app
from flask.cli import with_appcontext

from . import services as pulumi_services
from .services import create_pulumi_project_dir, pulumi_main_stack

@click.command(name='awscmd')
@click.argument('command')
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY override")
@with_appcontext
def awscmd(command, aws_kms_key):
    """
    Plumui aws script calls
    awscmd <command>
    e.g., "create-s3", "destroy-s3", "create-vpc", "destroy-vpc"
    """

    create_pulumi_project_dir(printf=click.echo)

    click.echo(f'Command: {command}')
    valid_cmds = {
        'create-s3', 'destroy-s3', 'create-vpc', 'destroy-vpc'
    }
    if command in valid_cmds:
        # Test we have AWS_KMS_KEY
        if (not aws_kms_key) and (('AWS_KMS_KEY' not in current_app.config) or not (current_app.config['AWS_KMS_KEY'])):
            click.echo("Must provide AWS_KMS_KEY via an Environment variable or by passing in command line!")
            sys.exit(1)
        else:
            if aws_kms_key:
                click.echo(f"AWS_KMS_KEY: {aws_kms_key}")
            else:
                click.echo(f"AWS_KMS_KEY: {current_app.config['AWS_KMS_KEY']}")

        if command == 'create-s3':
            pulumi_main_stack(printf=click.echo)
            # asyncio.run(pulumi_main_stack(printf=click.echo))
            # pulumi_services.init(pulumi_services.create_s3_bucket, app=current_app)
    #     elif command == 'destroy-s3':
    #         pulumi_services.init(pulumi_services.destroy_s3_bucket, app=current_app)
    # else:
    #     click.echo(f"Error: '{command}' is not a command!")


__commands__ = [
    awscmd,
]