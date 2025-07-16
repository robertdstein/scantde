from flask import Blueprint, request, render_template_string
from scantde.html.generate import generate_html_by_date
from scantde.server.index import DEFAULT_HTML

from datetime import datetime

date_bp = Blueprint('date', __name__)


@date_bp.route('/search_by_date', methods=['GET'])
def search_by_date():
    date = request.args.get('date', datetime.today().date().isoformat())
    datestr = date.replace('-', '')
    num_days = int(request.args.get('lookback_days', "1").strip())
    error = None
    html = DEFAULT_HTML
    # try:
    html = generate_html_by_date(datestr, lookback_days=num_days)

    return render_template_string(html, today=date, lookback_days=num_days)

# if __name__ == '__main__':
#     app.run(debug=True)