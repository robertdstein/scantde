import pandas as pd
from flask import Blueprint, render_template_string
from scantde.html.header import base_html_header

from datetime import datetime

index_bp = Blueprint('index', __name__)

DEFAULT_HTML = base_html_header(pd.DataFrame())


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string(
        DEFAULT_HTML,
        today=datetime.now().strftime('%Y-%m-%d')
    )