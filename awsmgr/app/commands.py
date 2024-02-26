# -*- coding: utf-8 -*-
"""Click commands."""
import os
import sys
from glob import glob
from subprocess import call
import pprint
import time
import shutil

import getpass
from pathlib import Path

from sqlalchemy.orm import sessionmaker
from flask.cli import with_appcontext
import click

from flask import current_app


command_script_path = Path(__file__).resolve()
command_script_dir = command_script_path.parent


# @click.command("collectstatic")
# @click.option('--no-input', is_flag=True, default=False, help='No input, will overrite existing path.')
# @with_appcontext
# def collectstatic(no_input):
#     overwrite = no_input
#     if no_input is False:
#         msg = """
#     This will overwrite existing files!
#     Are you sure you want to do this?
#     """
#         print(msg)
#         while not overwrite:
#             confirmation = click.prompt("Type 'yes' to continue, or 'no' to cancel", type=str)
#             if((confirmation.lower() == 'yes') or (confirmation.lower() == 'y')):
#                 overwrite = True
#             elif((confirmation.lower() == 'no') or (confirmation.lower() == 'n')):
#                 click.echo("Cancellation confirmed. Exiting.")
#                 raise click.Abort()
#             else:
#                 click.echo("Invalid input. Please type 'yes' or 'no'.")

#     if not overwrite:
#         return
#     static_dirs = [
#         command_script_dir / Path('static'),
#     ]
#     target_dir = current_app.config['STATIC_ROOT']

#     for static_dir in static_dirs:
#         shutil.copytree(static_dir, target_dir, dirs_exist_ok=True)

#     # ugly hack to move ./assets/img/favicon.ico -> STATIC_ROOT
#     shutil.copy2(command_script_dir / Path('../assets/img/favicon.ico'), target_dir)


# __commands__ = [collectstatic, ]
__commands__ = []
