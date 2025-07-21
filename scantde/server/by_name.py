from flask import Blueprint, request, render_template_string
from scantde.database.search import query_by_name
from scantde.html.generate import generate_html_by_name
from scantde.server.index import DEFAULT_HTML

from datetime import datetime

name_bp = Blueprint('name', __name__)


@name_bp.route('/search_by_name', methods=['GET'])
def search_by_name():
    name = request.args.get('name', '').strip()
    row = None
    columns = []
    error = ""
    extra_html = ""
    selection = request.args.get('selection', 'tdescore')
    if name:
        res = query_by_name(name, selection=selection)
        if res is not None:
            columns = sorted(res.index.tolist())
            row = res
            extra_html = generate_html_by_name(name, selection=selection)
        else:
            error = f"No result found for {name}"
    else:
        error = "Please enter a name."
    html = DEFAULT_HTML + '''
    {{ extra_html|safe }}
    {% if row is not none %}
    <h2>Database Results for: {{ row['name'] }}</h2>
      <table border="1">
        <tr><th>Field</th><th>Value</th></tr>
        {% for col in columns %}
          <tr><td>{{ col }}</td><td>{{ row[col] }}</td></tr>
        {% endfor %}
      </table>
    {% endif %}
    '''
    return render_template_string(html, row=row, columns=columns, error=error, extra_html=extra_html, today=datetime.now().strftime('%Y-%m-%d'), name=name, selection=selection)

# if __name__ == '__main__':
#     app.run(debug=True)