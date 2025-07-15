from flask import Blueprint, Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, select
from scantde.database.search import query_by_name, generate_html_by_name
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR
from pathlib import Path
from scantde.paths import sym_dir

from scantde.paths import db_path
#
# app = Flask(
#     __name__,
#     static_folder=str(sym_dir)
# )
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# db = SQLAlchemy(app)

from datetime import datetime, timedelta

index_bp = Blueprint('index', __name__)

HEADER_HTML = '''
<form method="post" action="/search_by_name">
  Search by Source Name: <input name="value">
  <button type="submit">Search by Name</button>
</form>
<form method="post" action="/search_by_date">
  Or Search by Date: <input type="date" name="date" value="{{ today }}">
  Number of days: <input type="number" name="num_days" min="1" value="1">
  <button type="submit">Search by Date</button>
</form>
'''


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    row = None
    columns = []
    error = None
    extra_html = ""
    results = []
    if request.method == 'POST':
        if 'search_name' in request.form:
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
        elif 'search_date' in request.form:
            date_str = request.form.get('date', '').strip()
            num_days = int(request.form.get('num_days', '1'))
            if date_str:
                try:
                    start_date = datetime.strptime(date_str, '%Y-%m-%d')
                    end_date = start_date + timedelta(days=num_days)
                    # results = query_by_date(start_date, end_date)
                    if not results:
                        error = f"No results found for {date_str} (+{num_days} days)"
                except Exception as e:
                    error = f"Invalid date: {e}"
            else:
                error = "Please enter a date."
    html = HEADER_HTML + '''
    {{ extra_html|safe }}
    {% if row is not none %}
    {% endif %}
    {% if results %}
    {% endif %}
      <table border="1">
        <tr><th>Result</th></tr>
        {% for r in results %}
        {% endfor %}
          <tr><td>{{ r }}</td></tr>
      </table>
      <table border="1">
        <tr><th>Field</th><th>Value</th></tr>
        {% for col in columns %}
        {% endfor %}
          <tr><td>{{ col }}</td><td>{{ row[col] }}</td></tr>
      </table>
    <p style="color:red;">{{ error }}</p>
    '''
    return render_template_string(html, row=row, columns=columns, error=error, extra_html=extra_html, results=results, today=datetime.now().strftime('%Y-%m-%d'))
#
# if __name__ == '__main__':
#     app.run(debug=True)