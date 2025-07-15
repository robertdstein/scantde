"""
Run the TDEScore selection for a given date
"""
import logging
from scantde.selections.tdescore.apply import apply_tdescore
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR

logger = logging.getLogger(__name__)


def run_tdescore(datestr, df):
    """
    Run the TDEScore selection for a given date

    :param datestr: Date to run the selection for
    :param df: Pandas DataFrame of candidates
    :return: None
    """

    nightly_output_dir = TDESCORE_HTML_DIR / datestr

    apply_tdescore(df, nightly_output_dir)

    logger.info(f"TDEScore complete for {datestr}!")