from flask import Blueprint, Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, select
from scantde.database.search import query_by_name, generate_html_by_name
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR
from pathlib import Path
from scantde.paths import sym_dir
from scantde.server.index import HEADER_HTML

from scantde.paths import db_path
#
# app = Flask(
#     __name__,
#     static_folder=str(sym_dir)
# )
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# db = SQLAlchemy(app)

from datetime import datetime, timedelta

name_bp = Blueprint('name', __name__)


@name_bp.route('/search_by_name', methods=['GET', 'POST'])
def search_by_name():
    row = None
    columns = []
    error = None
    extra_html = ""
    if request.method == 'POST':
        value = request.form['value'].strip()
        if value:
            res = query_by_name(value)
            if res is not None:
                columns = sorted(res.index.tolist())
                row = res
                extra_html = generate_html_by_name(value)
            else:
                error = f"No result found for {value}"
        else:
            error = "Please enter a name."
    html = HEADER_HTML + '''
    {{ extra_html|safe }}
    {% if row is not none %}
      <table border="1">
        <tr><th>Field</th><th>Value</th></tr>
        {% for col in columns %}
          <tr><td>{{ col }}</td><td>{{ row[col] }}</td></tr>
        {% endfor %}
      </table>
    {% endif %}
    <p style="color:red;">{{ error }}</p>
    '''
    return render_template_string(html, row=row, columns=columns, error=error, extra_html=extra_html, today=datetime.now().strftime('%Y-%m-%d'))

# if __name__ == '__main__':
#     app.run(debug=True)