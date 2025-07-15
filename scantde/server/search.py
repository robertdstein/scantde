from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, select
from scantde.database.search import query_by_name, generate_html_by_name
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR
from pathlib import Path
from scantde.paths import sym_dir

from scantde.paths import db_path

print(sym_dir)

app = Flask(
    __name__,
    static_folder=str(sym_dir)
)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    row = None
    columns = []
    error = None
    extra_html = ""
    if request.method == 'POST':
        value = request.form['value'].strip()
        res = query_by_name(value)
        if res is not None:
            columns = sorted(res.index.tolist())
            row = res
        else:
            error = f"No result found for {value}"
        extra_html = generate_html_by_name(value)
    html = '''
    <form method="post">
      Source Name: <input name="value">
      <input type="submit" value="Search">
    </form>
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
    return render_template_string(html, row=row, columns=columns, error=error, extra_html=extra_html)

if __name__ == '__main__':
    app.run(debug=True)