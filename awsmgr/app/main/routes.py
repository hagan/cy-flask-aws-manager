from flask import render_template, current_app

from awsmgr.app.main import bp


@bp.route('/')
def index():
    getfromconf = lambda X: current_app.config[X] if X in current_app.config else ''
    context = {
        # 'PUBLIC_KEY': getfromconf('PUBLIC_KEY'),
        # 'BEARER_TOKEN': getfromconf('BEARER_TOKEN'),
        # 'APPSTREAM_API': getfromconf('APPSTREAM_API'),
        # 'APPSTREAM_LAMBDA_ROOT_URL': getfromconf('APPSTREAM_LAMBDA_ROOT_URL'),
        # 'APPSTREAM_STREAMING_URL': getfromconf('APPSTREAM_STREAMING_URL'),
    }
    return render_template('index.html', **context)
