from flask import Blueprint

bp = Blueprint('main', __name__)

from awsmgr.app.blueprints.main import routes