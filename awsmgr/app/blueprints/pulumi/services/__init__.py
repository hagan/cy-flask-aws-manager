import os
import asyncio
from pathlib import Path

from pulumi.automation import LocalWorkspace, Stack, ProjectSettings, ProjectBackend

from awsmgr.app.utils import with_appcontext
from .s3bucket import pulumi_s3_bucket


@with_appcontext
def create_pulumi_project_dir(app, printf=print):
    pul_dir = app.config['PULUMI_PROJECT_DIR']
    dir_exists = Path(pul_dir).is_dir()
    
    if not dir_exists:
        try:
            printf(f"Creating pulumi {pul_dir} directory...")
            Path(pul_dir).mkdir()
            # os.makedirs(pul_dir, exist_ok=True)
        except Exception as e:
            printf(f"Error creating directory '{pul_dir}': {e}")
            return


@with_appcontext
def pulumi_main_stack(app, printf=print):
    ## @TODO: this is where we track state!
    project_name = "pulumi_over_automation"
    stack_name = "dev"
    # workspace = await LocalWorkspace.create(program=pulumi_s3_bucket) ## this is how remote would work, not for local tracking
    # printf(f"PULUMI_HOME: {app.config['PULUMI_HOME']}")
    # printf(f"PULUMI_PROJECT_DIR: {app.config['PULUMI_PROJECT_DIR']}")
    backend = ProjectBackend(f"file://{app.config['PULUMI_PROJECT_DIR']}")
    project_settings = ProjectSettings(
        project_name, "python",
        backend=backend
    )
    workspace = LocalWorkspace(
        program=pulumi_s3_bucket,
        project_settings=project_settings,
        pulumi_home=f"{app.config['PULUMI_HOME']}",
        # project_settings={
            
        #     "backend": {"url": f"file://{app.config['PULUMI_PROJECT_DIR']}"}
        # }
    )
    stacks = workspace.list_stacks()
    # stacks = asyncio.get_event_loop().run_until_complete(workspace.list_stacks())
    stack_names = [stack.name for stack in stacks]

    if stack_name in stack_names:
        stack = Stack.select(stack_name=stack_name, workspace=workspace)
    else:
        stack = Stack.create(stack_name=stack_name, workspace=workspace)

    stack.workspace.install_plugin("aws", "v4.0.0")
    stack.set_config("aws:region", value="us-west-2")

    up_result = stack.up()
    printf(f"Updated summary: \n{up_result.summary.resource_changes}")


__all__ = [
    create_pulumi_project_dir,
    pulumi_main_stack,
]