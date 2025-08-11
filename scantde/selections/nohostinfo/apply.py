"""
Module for integrating the TDEScore into the TDE pipeline.
(https://arxiv.org/abs/2312.00139)
"""

import logging
from pathlib import Path

import pandas as pd

from scantde.selections.utils.apply_thermal import apply_thermal
from scantde.log import export_processing_log,  update_source_list

from scantde.errors import NoSourcesError

from scantde.selections.utils.export import export_results
from scantde.selections.utils.algorithmic_cuts import apply_algorithmic_cuts
from scantde.selections.utils.download import download_data
from scantde.selections.utils.apply_lightcurve import apply_lightcurve
from scantde.utils.skyportal import export_to_skyportal
from scantde.utils.slack import send_to_slack


logger = logging.getLogger(__name__)


NOHOST_SELECTION = "tdescore_nohostinfo"


def apply_tdescore_nohostinfo(
    df: pd.DataFrame,
    base_output_dir: Path,
):
    """
    Function to apply the TDEScore to a table of sources

    :param df: Table of sources
    :param base_output_dir: Directory to save output
    """

    datestr = base_output_dir.name
    proc_log = []

    logger.info(f"Running selection {NOHOST_SELECTION} for {datestr}")

    if len(df) == 0:
        logger.warning("Source table is empty, generating empty HTML table")
        return pd.DataFrame()

    try:

        df, _, proc_log = apply_algorithmic_cuts(
            df, selection=NOHOST_SELECTION, proc_log=proc_log,
            require_nuclear=True, require_multidet=False
        )

        df, full_df, proc_log = download_data(
            df, datestr=datestr, selection=NOHOST_SELECTION, proc_log=proc_log
        )

        apply_lightcurve(
            df, base_output_dir=base_output_dir,
        )

        df = apply_thermal(
            df, selection=NOHOST_SELECTION, base_output_dir=base_output_dir,
        )

        mask = pd.notnull(df["tdescore"])

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=NOHOST_SELECTION,
            stage="LC Fit failed"
        )

        if len(df) == 0:
            raise NoSourcesError("No sources left after lightcurve fit")

        full_df = export_results(df, datestr=datestr, selection=NOHOST_SELECTION)


        # Export sources to SkyPortal
        export_to_skyportal(full_df[~full_df["is_junk"]])

        logger.info(df)

    except NoSourcesError:
        logger.warning("Terminated early due to lack of sources")
        df = pd.DataFrame()

    # Send to slack
    send_to_slack(datestr=datestr, selection=NOHOST_SELECTION)

    export_processing_log(proc_log, datestr=datestr, selection=NOHOST_SELECTION)
    return df

