from flask import Blueprint, Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table, select
from scantde.database.search import generate_html_by_date
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

date_bp = Blueprint('date', __name__)


@date_bp.route('/search_by_date', methods=['GET', 'POST'])
def search_by_date():
    error = None
    extra_html = ""
    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        num_days = int(request.form.get('num_days', '1'))
        if date_str:
            try:
                start_date = datetime.strptime(date_str, '%Y-%m-%d')
                datestr = start_date.strftime('%Y%m%d')
                extra_html = generate_html_by_date(datestr, lookback_days=num_days)
                # end_date = start_date + timedelta(days=num_days)
                # results = query_by_date(start_date, end_date)
                # if not results:
                #     error = f"No results found for {date_str} (+{num_days} days)"
            except Exception as e:
            # except KeyboardInterrupt:
                error = f"Invalid date: {e}"
        else:
            error = "Please enter a date."
    html = HEADER_HTML + '''
    {{ extra_html|safe }}
    '''
    return render_template_string(html, error=error, extra_html=extra_html, today=datetime.now().strftime('%Y-%m-%d'))

# if __name__ == '__main__':
#     app.run(debug=True)