from flask import Blueprint

bp = Blueprint('main', __name__)

from awsmgr.app.main import routes