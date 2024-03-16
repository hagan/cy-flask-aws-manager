import os
import asyncio
from pathlib import Path
from typing import Callable

from flask import current_app
from flask.cli import with_appcontext

from pulumi_aws import Provider
from pulumi.automation import LocalWorkspace, Stack, ProjectSettings, ProjectBackend, ConfigValue

from awsmgr.app.blueprints.boto.services.dataclass import AWSMgrConfigDataClass

## with_appcontext sets functions 'app' argument to current_app from flask
# Note, anything that references this will need to be from flask or use:
# with app.app_context():
# from awsmgr.app.utils import with_appcontext
# from awsmgr.app import create_app

# from .s3bucket import pulumi_s3_bucket
# from .ec2instance import pulumi_ec2_instance


SetupStackFunction = Callable[[], None]


def create_dir(
    dir_path=None,
    printf=print
):
    if dir_path is None:
        raise Exception("ERROR: 'dir_path' was set to None")
    dir_exists = Path(dir_path).is_dir()

    if not dir_exists:
        try:
            # printf(f"Creating pulumi {dir_path} directory...")
            Path(dir_path).mkdir()
            # os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            # printf(f"Error creating directory '{dir_path}': {e}")
            return


def get_pulumi_provider(acdc: AWSMgrConfigDataClass):
    """
    Setup AWS Provider
    """
    print("get_pulumi_provider()")
    return Provider(
        "aws-provider",
        access_key=acdc.aws_access_key_id,
        secret_key=acdc.aws_secret_access_key,
        token=acdc.aws_session_token,
        region=acdc.aws_default_region
    )



def pulumi_setup_stack_call(
    acdc: AWSMgrConfigDataClass,
    program: SetupStackFunction,
    project_name: str,
    stack_name: str,
    pulumi_project_dir: str,
    pulumi_home_dir: str,
    setup: bool = True,
    printf=print
):
    backend = ProjectBackend(pulumi_project_dir)
    project_settings = ProjectSettings(
        project_name, "python",
        backend=backend
    )
    workspace = LocalWorkspace(
        program=program,
        project_settings=project_settings,
        pulumi_home=pulumi_home_dir,
    )
    stacks = workspace.list_stacks()
    stack_names = [stack.name for stack in stacks]
    if stack_name in stack_names:
        printf("BEFORE ISSUE A")
        stack = Stack.select(stack_name=stack_name, workspace=workspace)
    else:
        printf("BEFORE ISSUE B")
        stack = Stack.create(stack_name=stack_name, workspace=workspace)

    printf("and here C")
    stack.workspace.install_plugin("aws", "v4.0.0")
    # stack.set_config("aws:region", value="us-west-2", secret=False)
    printf("and here D")
    stack.set_config("aws:region", ConfigValue(value=acdc.aws_default_region, secret=False))
    printf("and here E")
    if setup:
        up_result = stack.up(on_output=printf)
        printf(f"Up result: \n{up_result.summary.resource_changes}")
    else:
        destroy_result = stack.destroy(on_output=printf)
        printf(f"Destroy result: \n{destroy_result.summary.resource_changes}")


# @with_appcontext
# def pulumi_main_stack(
#     command,
#     aws_kms_key=None,
#     project_name=None,
#     stack_name=None,
#     pulumi_project_dir=None,
#     pulumi_home_dir=None,
#     aws_region=None,
#     printf=print
# ):
#     ## @TODO: this is where we track state!
#     # project_name = "pulumi_over_automation"
#     # stack_name = "dev"
#     # pulumi_project_dir = f"file://{current_app.config['PULUMI_PROJECT_DIR']}"
#     # pulumi_home_dir = f"{current_app.config['PULUMI_HOME']}"
#     # aws_region = f"{current_app.config['AWS_REGION']}"
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)
#     # loop.run_until_complete(pulumi_setup_stack_call(project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region))
#     # loop.close()

#     if command == 'create-s3':
#         printf("Creating s3 stack...")
#         pulumi_setup_stack_call(pulumi_s3_bucket, project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region, printf=printf)
#     elif command == 'destroy-s3':
#         printf("Destroying s3 stack...")
#         pulumi_setup_stack_call(pulumi_s3_bucket, project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region, setup=False, printf=printf)
#     elif command == 'create-ec2':
#         printf("Creating ec2 instance...")
#         pulumi_setup_stack_call(pulumi_ec2_instance, project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region, printf=printf)
#     elif command == 'destroy-ec2':
#         printf("Destroying ec2 instance...")
#         pulumi_setup_stack_call(pulumi_ec2_instance, project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region, setup=False, printf=printf)
#     else:
#         printf("Unregcognized command: '{command}'")


    # if command == 'create-s3':
    #     up_result = stack.up()
    #     printf(f"Up result: \n{up_result.summary.resource_changes}")
    # elif command == 'destroy-s3':
    #     destroy_result = stack.destroy()
    #     printf(f"Destroy result: \n{destroy_result.summary.resource_changes}")


__all__ = [
    create_dir,
    pulumi_setup_stack_call,
]