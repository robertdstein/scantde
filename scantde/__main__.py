"""
Run the TDEScore integration for a given date
"""

import argparse
import logging

from scantde.utils import get_current_datestr
from tdescore.combine.parse import combine_all_sources

from scantde.candidates import get_ztf_candidates, ztf_alerts_path
from scantde.utils import get_known_tdes
from scantde.selections.tdescore.apply import apply_tdescore
from scantde.selections.nohostinfo.apply import apply_tdescore_nohostinfo
from scantde.paths import base_html_dir

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
        "-s", "--skip", help="Skip the lightcurve", default=False, action="store_true"
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

    df["tdescore_lc"] = args.skip

    all_known_tdes = get_known_tdes()
    logger.info(f"Have {len(all_known_tdes)} known TDEs")

    df["latest_datestr"] = datestr
    df["source_name"] = df["name"]
    df.set_index("source_name", inplace=True)
    df["is_tde"] = df["name"].isin(all_known_tdes)

    df["tdescore"] = None
    df["tdescore_best"] = None
    df["tdescore_high_noise"] = False
    df["tdescore_lc_score"] = None

    df = df.sort_values(by=["is_tde", "name"], ascending=[False, False])
    df.reset_index(drop=True, inplace=True)

    if args.debug:
        df = df[:2000]

    nightly_output_dir = base_html_dir / datestr
    nightly_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running TDEScore integration for {datestr}")

    # # Apply tdescore (classic)
    # proc_df = apply_tdescore(df.copy(), base_output_dir=nightly_output_dir)
    #
    # # Do not repeat lightcurve analysis for already processed sources
    # if len(proc_df) > 0:
    #     mask = df["ztf_name"].isin(proc_df["ztf_name"])
    #     df.loc[mask, "tdescore_lc"] = True

    # Apply tdescore (no host info)
    apply_tdescore_nohostinfo(df.copy(), base_output_dir=nightly_output_dir)
