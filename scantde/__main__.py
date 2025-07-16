"""
Run the TDEScore integration for a given date
"""

import argparse
import logging
import scantde.selections.tdescore

# Set the TDESCORE_DATA environment variable to the output directory
import os
# from scantde.paths import tdescore_output_dir
# os.environ["TDESCORE_DATA"] = str(tdescore_output_dir)

from scantde.utils import get_current_datestr
from scantde.selections.tdescore.io import load_candidates
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR, make_daily_html_table
from scantde.selections.tdescore.archive import update_archive
from tdescore.combine.parse import combine_all_sources

from scantde.candidates import get_ztf_candidates, ztf_alerts_path
from scantde.utils import get_known_tdes
from scantde.selections.tdescore.run import run_tdescore

logger = logging.getLogger(__name__)


def run():
    """
    Run the TDEScore integration for a given date
    """
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("scantde").setLevel(logging.INFO)
    logging.getLogger("tdescore").setLevel(logging.INFO)

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-n", "--night", "--datestr",
        type=str, help="Date to run the integration for", required=False,
        dest="night"
    )
    argparser.add_argument(
        "-s", "--skip", help="Skip the download", default=False, action="store_true"
    )
    argparser.add_argument(
        "--debug", help="Run in debug mode", default=False, action="store_true"
    )
    args = argparser.parse_args()

    datestr = args.night

    if datestr is None:
        datestr = get_current_datestr()

    if (not args.debug) & (not args.skip):
        # Remove the nightly file to force a re-download
        ztf_cache = ztf_alerts_path(datestr)
        if ztf_cache.is_file():
            logger.info(f"Re-downloading initial candidates for {datestr}")
            ztf_cache.unlink(missing_ok=True)
        else:
            logger.info(f"Downloading initial candidates for {datestr}")

    df = get_ztf_candidates(datestr)

    df["tdescore_lc"] = False

    all_known_tdes = get_known_tdes()
    logger.info(f"Have {len(all_known_tdes)} known TDEs")

    df["latest_datestr"] = datestr
    df["source_name"] = df["name"]
    df.set_index("source_name", inplace=True)
    df["is_tde"] = df["name"].isin(all_known_tdes)

    df = df.sort_values(by=["is_tde", "name"], ascending=[False, False])
    df.reset_index(drop=True, inplace=True)

    if args.debug:
        df = df[:2000]

    logger.info(f"Running TDEScore integration for {datestr}")
    run_tdescore(datestr, df)


def rebuild_html():
    """
    Run the TDEScore integration for a given date
    """

    logger.setLevel(logging.INFO)
    logging.getLogger("scantde").setLevel(logging.INFO)

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-n", "--night", "--datestr",
        dest="datestr",
        type=str, help="Date to run the integration for", required=False
    )
    args = argparser.parse_args()

    datestr = args.datestr

    if datestr is None:
        datestr = get_current_datestr()

    logger.info(f"Re-building html for {datestr}")

    df = load_candidates(datestr)
    full_df = combine_all_sources(df, save=False)

    html_output_dir = TDESCORE_HTML_DIR / datestr

    make_daily_html_table(full_df, output_dir=html_output_dir)
    update_archive(datestr)
