import json
import os

import pulumi
from pulumi import automation as auto

import sys

# config = pulumi.Config()
# env = pulumi.get_stack()
# vpc_name = config.require("cyverse-ec2-example-vpc")
# zone_number = config.require_int("zone_number")
# vpc_cidr = config.require("vpc_cidr")

def pulumi_program():
    # Importing inside the function to avoid loading issues when the automation API rehydrates the program
    import pulumi_aws as aws

    # Create an AWS S3 bucket
    bucket = aws.s3.Bucket('myBucket')

    # Export the bucket's name
    pulumi.export('bucket_name', bucket.id)


def init(app=None):
    """
    This calls AWS services with pulumi
    """
    destroy = True
    if app is None:
        return

    project_name = app.config['PULUMI_PROJECT_NAME']
    project_dir = app.config['PULUMI_PROJECT_DIR']
    stack_name = app.config['PULUMI_STACK_NAME']
    project_template = app.config['PULUMI_PROJECT_TEMPLATE']
    pulumi_home = app.config['PULUMI_HOME']

    aws_region = app.config['AWS_REGION']
    aws_kms_env = app.config['AWS_KMS_KEY']
    

    print("Initalizing up pulumni service")
    print(f"PULUMI_PROJECT_NAME: {project_name}")
    print(f"PULUMI_PROJECT_DIR: {project_dir}")
    print(f"PULUMI_STACK_NAME: {stack_name}")
    print(f"PULUMI_PROJECT_TEMPLATE: {project_template}")
    print(f"PULUMI_HOME: {pulumi_home}")

    print(f"AWS_REGION: {aws_region}")

    # print(f"PULUMI_USER_CONFIG_DIR: {app.config['PULUMI_USER_CONFIG_DIR']}")

    try:
        os.makedirs(app.config['PULUMI_PROJECT_DIR'], exist_ok=True)
    except Exception as e:
        print(f"Error creating directory '{app.config['PULUMI_PROJECT_DIR']}': {e}")
        return

    project_settings = auto.ProjectSettings(
        name=project_name,
        runtime='python',
        backend={'url': f"file://{project_dir}"}
    )
    secrets_provider = "awskms://aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee?region=us-west-2"
    if aws_kms_env:
        secrets_provider = f"awskms://{aws_kms_env}?region={aws_region}"
    else:
        raise Exception("Please provide the AWS_KMS_KEY to aquire the secrets_provider string!")

    stack_settings = auto.StackSettings(
        secrets_provider=secrets_provider
    )

    # Initialize the workspace and select/create the stack
    # workspace = auto.LocalWorkspace(project_settings=project_settings, program=pulumi_program)
    stack = auto.create_or_select_stack(
        stack_name=stack_name,
        project_name=project_name,
        program=pulumi_program,
        opts=auto.LocalWorkspaceOptions(
            project_settings=project_settings,
            secrets_provider=secrets_provider,
            stack_settings={"dev": stack_settings}
        )
    )
    print("Successfully initialized stack")

    # for inline programs, we must manage plugins ourself
    stack.workspace.install_plugin("aws", "v6.18.2")
    stack.workspace.install_plugin("awsx", "v2.4.0")
    print("Plugins installed...")
    # Set stack configuration specifying the AWS region to deploy
    print("setting up stack...")
    stack.set_config("aws:region", auto.ConfigValue(value=aws_region))
    print("config set")

    print("refreshing stack...")
    stack.refresh(on_output=print)
    print("refresh complete!")

    if destroy:
        print("destroying stack...")
        stack.destroy(on_output=print)
        print("stack destroy complete")
        sys.exit()

    print("updating/setting up stack...")
    up_res = stack.up(on_output=print)
    print(
        "update summary: \n"
        f"{json.dumps(up_res.summary.resource_changes, indent=4)}"
    )

    print(f"Project {project_name} created successfully in {project_dir}")
