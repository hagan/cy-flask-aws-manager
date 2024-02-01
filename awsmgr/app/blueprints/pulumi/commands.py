import click
import sys

from flask import current_app
from flask.cli import with_appcontext

from . import services as pulumi_services


@click.command('awscmd')
@click.argument('command')
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY override")
@with_appcontext
def awscmd(command, aws_kms_key):
    """
    Our flask cli handler for testing our pulumni commands
    """
    print(f"command: {command}")
    print(f"aws_kms_key: {aws_kms_key}")
    valid_cmds = {
        'create-s3', 'destroy-s3', 'create-vpc', 'destroy-vpc'
    }
    if command in valid_cmds:
        # Test we have AWS_KMS_KEY
        if (not aws_kms_key) and ()'AWS_KMS_KEY' not in current_app.config or not (current_app.config['AWS_KMS_KEY'])):
            click.echo("Must provide AWS_KMS_KEY via an Environment variable or by passing in command line!")
            sys.exit(1)
        else:
            if aws_kms_key:
                click.echo(f"AWS_KMS_KEY: {aws_kms_key}")
            else:
                click.echo(f"AWS_KMS_KEY: {current_app.config['AWS_KMS_KEY']}")


        click.echo(f'awscmd - {command}')
        if command == 'create-s3':
            pulumi_services.init(pulumi_services.create_s3_bucket, app=current_app)
    else:
        click.echo(f"Error: '{command}' is not a command!")


__commands__ = [
    awscmd,
]