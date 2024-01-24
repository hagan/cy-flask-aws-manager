# -*- coding: utf-8 -*-
"""Create an application instance."""

from awsmgr.app import create_app
from flask.awsmgr import config as awsmgr_config

app = create_app(config_class=awsmgr_config)
