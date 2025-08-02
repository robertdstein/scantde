"""
Module for integrating the TDEScore into the TDE pipeline.
(https://arxiv.org/abs/2312.00139)
"""

import logging
from pathlib import Path

import pandas as pd


from tdescore.download.tns import download_tns_data
from tdescore.lightcurve.analyse import batch_analyse, batch_analyse_thermal
from tdescore.lightcurve.thermal import THERMAL_WINDOWS
from tdescore.paths import data_dir, sfd_path
from tdescore.raw import load_raw_sources
from tdescore.raw.extract import combine_raw_source_data
from tdescore.raw.ztf import download_alert_data, ZTF_BACKEND
from tdescore.sncosmo.run_sncosmo import batch_sncosmo
from tdescore.lightcurve.thermal import (
    analyse_source_thermal
)

from scantde.selections.utils.algorithmic_cuts import apply_algorithmic_cuts
from scantde.selections.utils.classifiers import apply_classifier
from scantde.utils.skyportal import export_to_skyportal
from scantde.log import export_processing_log

from scantde.log import update_source_list
from scantde.errors import NoSourcesError
from scantde.selections.utils.apply_thermal import apply_thermal
from scantde.selections.utils.download import download_data
from scantde.selections.utils.export import export_results
from scantde.selections.utils.apply_lightcurve import apply_lightcurve
from scantde.selections.utils.apply_infant import apply_infant
from scantde.selections.utils.apply_full import apply_full
from scantde.utils.slack import publish


logger = logging.getLogger(__name__)


TDESCORE_SELECTION = "tdescore"


def apply_tdescore(
    df: pd.DataFrame,
    base_output_dir: Path,
):
    """
    Function to apply the TDEScore to a table of sources

    :param df: Table of sources
    :param base_output_dir: Directory to save output
    """

    datestr = base_output_dir.name

    logger.info(f"Running selection {TDESCORE_SELECTION} for {datestr}")

    proc_log = []

    if len(df) == 0:
        logger.warning("Source table is empty, generating empty HTML table")
        return pd.DataFrame()

    try:
        df, full_df, proc_log = apply_algorithmic_cuts(
            df, selection=TDESCORE_SELECTION, proc_log=proc_log,
            require_nuclear=True, require_multidet=False
        )

        # Apply the host classifier, which includes WISE data
        scores, nan_mask = apply_classifier(
            full_df, "host", selection=TDESCORE_SELECTION, explain=False
        )
        df, proc_log = update_source_list(
            df, proc_log, ~nan_mask, selection=TDESCORE_SELECTION,
            stage="TDEScore nans with full host data"
        )
        df["tdescore_host"] = scores
        mask = df["tdescore_host"] > 0.0001
        df, proc_log = update_source_list(
            df, proc_log, mask, selection=TDESCORE_SELECTION,
            stage="TDEScore cuts with full crossmatch data"
        )

        # Now we have the host classifier applied, we can download the data
        df, full_df, proc_log = download_data(
            df, datestr=datestr, selection=TDESCORE_SELECTION, proc_log=proc_log
        )

        apply_lightcurve(
            df, base_output_dir=base_output_dir,
        )

        df = apply_full(
            df, base_output_dir=base_output_dir, selection=TDESCORE_SELECTION,
        )

        df, proc_log = apply_infant(
            df, selection=TDESCORE_SELECTION, base_output_dir=base_output_dir, proc_log=proc_log,
        )

        df = apply_thermal(
            df, selection=TDESCORE_SELECTION, base_output_dir=base_output_dir,
        )

        full_df = export_results(df, datestr=datestr, selection=TDESCORE_SELECTION)

        # Send to slack
        publish(
            datestr=datestr,
            selection=TDESCORE_SELECTION,
        )

        # Export sources to SkyPortal
        export_to_skyportal(full_df[~full_df["is_junk"]])
        logger.info(df)

    except NoSourcesError:
        logger.warning("Terminated early due to lack of sources")
        df = pd.DataFrame()

    export_processing_log(proc_log, datestr=datestr, selection=TDESCORE_SELECTION)
    return df

