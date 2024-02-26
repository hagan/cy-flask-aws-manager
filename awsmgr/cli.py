# -*- coding: utf-8 -*-
"""Click commands."""

import sys
import os
import pprint
import click

# from flask import Flask

# from awsmgr.app import create_app
from awsmgr.app.blueprints.pulumi.commands import base_awscmd

from awsmgr.config import Config

# app = create_app()

@click.command()
@click.argument('command')
@click.option('--aws-kms-key', default=None, help="AWS_KMS_KEY override")
def awsmgr(command, aws_kms_key):
    """
    Plumui aws script calls
    awscmd <command>
    e.g., "create-s3", "destroy-s3", "create-vpc", "destroy-vpc"
    """
    # with app.app_context():
    #     click.echo("awsmgr app context should be setup now.")
    ## @TODO: somehow get our flask app config
    # app = Flask(__name__)
    # app.config.from_object(Config)
    flask_settings = Config.__dict__

    if aws_kms_key is None:
        aws_kms_key = f"{flask_settings['AWS_KMS_KEY']}"

    project_name = "pulumi_over_automation"
    stack_name = "dev"
    pulumi_project_dir = f"file://{flask_settings['PULUMI_PROJECT_DIR']}"
    pulumi_home_dir = f"{flask_settings['PULUMI_HOME']}"
    aws_region = f"{flask_settings['AWS_REGION']}"

    base_awscmd(
        command,
        aws_kms_key=aws_kms_key,
        project_name=project_name,
        stack_name=stack_name,
        pulumi_project_dir=pulumi_project_dir,
        pulumi_home_dir=pulumi_home_dir,
        aws_region=aws_region
    )

if __name__ == "__main__":
    awsmgr()
