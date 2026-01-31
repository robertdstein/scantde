from flask import Blueprint, request, render_template_string
from scantde.htmlutils.generate import generate_html_by_date
from scantde.server.index import DEFAULT_HTML
# from scantde.server.login import login_required
from scantde.errors import MissingCacheError

from datetime import datetime

date_bp = Blueprint('date', __name__)

@date_bp.route('/search_by_date', methods=['GET'])
# @login_required
def search_by_date() -> str:
    """
    Search for candidates by date and generate HTML output.

    :return: HTML output for the specified date.
    """
    date = request.args.get('date', datetime.today().date().isoformat())
    datestr = date.replace('-', '')
    num_days = int(request.args.get('lookback_days', "1").strip())
    min_score = float(request.args.get('min_score', 0.01).strip())
    hide_junk = bool(request.args.get('hide_junk'))
    hide_classified = bool(request.args.get('hide_classified', False))
    mode = request.args.get('mode', 'all')
    selection = request.args.get('selection', 'tdescore')
    show_cutout = bool(request.args.get('show_cutout', False))
    error = ""
    html = DEFAULT_HTML
    try:
        html = generate_html_by_date(
            datestr, selection=selection, lookback_days=num_days,
            min_score=min_score,
            hide_junk=hide_junk,
            hide_classified=hide_classified,
            mode=mode, include_cutout=show_cutout
        )
    except MissingCacheError:
        error = f"No cached results found for {date}. Please try a different date."

    return render_template_string(html, today=date, lookback_days=num_days, min_score=min_score, hide_junk=hide_junk, hide_classified=hide_classified, error=error, mode=mode, selection=selection, show_cutout=show_cutout)