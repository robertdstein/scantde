"""
Module for integrating the TDEScore into the TDE pipeline.
(https://arxiv.org/abs/2312.00139)
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.time import Time
from tqdm import tqdm

from tdescore.combine.parse import combine_all_sources
from tdescore.download.all import (
    download_all,
    download_fritz_data,
    download_gaia_data,
    download_panstarrs_data,
    download_ps1strm_data,
    download_sdss_data,
    download_tns_data,
    download_wise_data,
    download_legacy_survey_data,
)
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

from scantde.selections.utils.apply_thermal import apply_thermal
from scantde.utils.plot import create_lightcurve_plots
from scantde.utils.skyportal import export_to_skyportal, download_from_skyportal
from scantde.log import export_processing_log, update_processing_log, update_source_list

from scantde.errors import NoSourcesError

from scantde.selections.utils.export import export_results
from scantde.selections.utils.algorithmic_cuts import apply_algorithmic_cuts
from scantde.selections.utils.download import download_data


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

    if len(df) == 0:
        logger.warning("Source table is empty, generating empty HTML table")
        return pd.DataFrame()

    try:

        df, _, proc_log = apply_algorithmic_cuts(
            df, selection=NOHOST_SELECTION, proc_log=proc_log,
            require_nuclear=True,
        )

        df, full_df, proc_log = download_data(
            df, datestr=datestr, selection=NOHOST_SELECTION, proc_log=proc_log
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
        # export_to_skyportal(full_df[~mask])

        logger.info(df)

    except NoSourcesError:
        logger.warning("Terminated early due to lack of sources")
        df = pd.DataFrame()

    export_processing_log(proc_log, datestr=datestr, selection=NOHOST_SELECTION)
    return df

