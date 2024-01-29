import click

from flask import current_app
from flask.cli import with_appcontext

from . import services as pulumi_services


@click.command('pulumi-setup')
@with_appcontext
def pulumi_setup():
    click.echo('Configuring pulumi')
    pulumi_services.init(app=current_app)


@click.command('vpc-setup')
@with_appcontext
def vpc_setup():
    """
    @TODO: This needs to stand up a VPC for our EC2's to exist in so we can 
    use one elastic IP to connect into the system from the outside.

    Will also want to attaching billing tags / project tags
    """
    click.echo('Setting up VPC')
    # pulumi_services.pulumi_services()


@click.command('vpc-teardown')
@with_appcontext
def vpc_teardown():
    """
    @TODO: This needs to teardown a VPC for our EC2's. This should check
    if there are any existing systems using service and stop or ask to confirm.

    Will also want to attaching billing tags / project tags
    """
    click.echo('Tearing down VPC')

__commands__ = [
    pulumi_setup,
    vpc_setup,
    vpc_teardown,
]