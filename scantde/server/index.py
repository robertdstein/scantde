import pandas as pd
from flask import Blueprint, render_template_string
from scantde.htmlutils.header import base_html_header
# from scantde.server.login import login_required

from datetime import datetime

index_bp = Blueprint('index', __name__)

DEFAULT_HTML = base_html_header(pd.DataFrame())

@index_bp.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    return render_template_string(
        DEFAULT_HTML,
        today=datetime.now().strftime('%Y-%m-%d')
    )

from flask import request, session

@index_bp.route("/ping")
def ping():
    return "pong"

@index_bp.route("/whoami")
def whoami():
    return f"path={request.path}, logged_in={session.get('logged_in')}"