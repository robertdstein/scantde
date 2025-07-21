from flask import Blueprint, request, render_template_string
from scantde.html.generate import generate_html_by_date
from scantde.server.index import DEFAULT_HTML
from scantde.server.login import login_required

from datetime import datetime

date_bp = Blueprint('date', __name__)

@date_bp.route('/search_by_date', methods=['GET'])
@login_required
def search_by_date() -> str:
    """
    Search for candidates by date and generate HTML output.

    :return: HTML output for the specified date.
    """
    date = request.args.get('date', datetime.today().date().isoformat())
    datestr = date.replace('-', '')
    num_days = int(request.args.get('lookback_days', "1").strip())
    hide_junk = bool(request.args.get('hide_junk'))
    mode = request.args.get('mode', 'all')
    selection = request.args.get('selection', 'tdescore')
    show_cutout = bool(request.args.get('show_cutout', False))
    error = ""
    html = DEFAULT_HTML
    try:
        html = generate_html_by_date(
            datestr, selection=selection, lookback_days=num_days, hide_junk=hide_junk,
            mode=mode, include_cutout=show_cutout
        )
    except FileNotFoundError:
        error = f"No cached results found for {date}. Please try a different date."

    return render_template_string(html, today=date, lookback_days=num_days, hide_junk=hide_junk, error=error, mode=mode, selection=selection, show_cutout=show_cutout)