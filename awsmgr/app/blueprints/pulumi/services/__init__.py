import os
import asyncio
from pathlib import Path

from flask import current_app
from flask.cli import with_appcontext

from pulumi.automation import LocalWorkspace, Stack, ProjectSettings, ProjectBackend, ConfigValue

## with_appcontext sets functions 'app' argument to current_app from flask
# Note, anything that references this will need to be from flask or use:
# with app.app_context():
# from awsmgr.app.utils import with_appcontext
# from awsmgr.app import create_app

from .s3bucket import pulumi_s3_bucket


# app = create_app()


# @with_appcontext
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

async def setup_stack(
    project_name,
    stack_name,
    pulumi_project_dir,
    pulumi_home_dir,
    aws_region
):
    backend = ProjectBackend(pulumi_project_dir)
    project_settings = ProjectSettings(
        project_name, "python",
        backend=backend
    )
    workspace = LocalWorkspace(
        program=pulumi_s3_bucket,
        project_settings=project_settings,
        pulumi_home=pulumi_home_dir,
    )
    stacks = workspace.list_stacks()
    stack_names = [stack.name for stack in stacks]
    if stack_name in stack_names:
        print("BEFORE ISSUE A")
        stack = Stack.select(stack_name=stack_name, workspace=workspace)
    else:
        print("BEFORE ISSUE B")
        stack = Stack.create(stack_name=stack_name, workspace=workspace)

    print("and here C")
    stack.workspace.install_plugin("aws", "v4.0.0")
    # stack.set_config("aws:region", value="us-west-2", secret=False)
    print("and here D")
    stack.set_config("aws:region", ConfigValue(value=aws_region, secret=False))
    print("and here E")
    up_result = await stack.up()
    print(f"Up result: \n{up_result.summary.resource_changes}")


# @with_appcontext
def pulumi_main_stack(
    command,
    aws_kms_key=None,
    project_name=None,
    stack_name=None,
    pulumi_project_dir=None,
    pulumi_home_dir=None,
    aws_region=None,
    printf=print
):
    ## @TODO: this is where we track state!
    # project_name = "pulumi_over_automation"
    # stack_name = "dev"
    # pulumi_project_dir = f"file://{current_app.config['PULUMI_PROJECT_DIR']}"
    # pulumi_home_dir = f"{current_app.config['PULUMI_HOME']}"
    # aws_region = f"{current_app.config['AWS_REGION']}"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_stack(project_name, stack_name, pulumi_project_dir, pulumi_home_dir, aws_region))
    loop.close()

    # if command == 'create-s3':
    #     up_result = stack.up()
    #     printf(f"Up result: \n{up_result.summary.resource_changes}")
    # elif command == 'destroy-s3':
    #     destroy_result = stack.destroy()
    #     printf(f"Destroy result: \n{destroy_result.summary.resource_changes}")


__all__ = [
    create_dir,
    pulumi_main_stack,
]