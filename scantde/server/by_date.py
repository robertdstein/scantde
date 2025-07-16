from flask import Blueprint, request, render_template_string
from scantde.html.generate import generate_html_by_date
from scantde.server.index import DEFAULT_HTML

from datetime import datetime

date_bp = Blueprint('date', __name__)


@date_bp.route('/search_by_date', methods=['GET'])
def search_by_date():
    datestr = request.args.get('date', '').strip().replace('-', '')
    num_days = int(request.args.get('lookback_days', "1").strip())
    error = None
    html = DEFAULT_HTML
    # try:
    html = generate_html_by_date(datestr, lookback_days=num_days)
    # except Exception as e:
    #     error = f"Invalid date: {e}"
    return render_template_string(html, error=error, today=datetime.now().strftime('%Y-%m-%d'))

# if __name__ == '__main__':
#     app.run(debug=True)