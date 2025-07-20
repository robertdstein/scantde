"""
Run the TDEScore selection for a given date
"""
import logging
from scantde.selections.nohostinfo.apply import apply_tdescore_nohostinfo
from scantde.html.make_html import TDESCORE_HTML_DIR

logger = logging.getLogger(__name__)


def run_tdescore_nohostinfo(datestr, df):
    """
    Run the TDEScore selection for a given date

    :param datestr: Date to run the selection for
    :param df: Pandas DataFrame of candidates
    :return: None
    """

    nightly_output_dir = TDESCORE_HTML_DIR / datestr

    apply_tdescore_nohostinfo(df, nightly_output_dir)

    logger.info(f"TDEScore complete for {datestr}!")