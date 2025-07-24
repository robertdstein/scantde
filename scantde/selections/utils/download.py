import pandas as pd

import logging


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

from scantde.utils.skyportal import download_from_skyportal

from scantde.log import update_source_list

from scantde.log.model import ProcStage

from tdescore.combine.parse import combine_all_sources
from tdescore.download.all import download_legacy_survey_data

from scantde.selections.utils.extinction import append_extinction_to_df

from astropy.time import Time

logger = logging.getLogger(__name__)

def download_data(
    df: pd.DataFrame,
    datestr: str,
    selection: str,
    proc_log: list[ProcStage],
):

    t_max_jd = Time(
        f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}T15:00:00.0", format='isot'
    ).jd

    # Download all the alert data up to the specific night
    logger.info(f"Downloading full lightcurve data using backend {ZTF_BACKEND}")
    passed_names = download_alert_data(
        df["ztf_name"][~df["tdescore_lc"]], overwrite=True, t_max_jd=t_max_jd
    )

    mask = df["ztf_name"].isin(passed_names) | df["tdescore_lc"]

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Has lightcurve data"
    )

    # Download skyportal data (redshift, tns_name, classifications)
    df = download_from_skyportal(df)

    # Download legacy survey data (redshift - either specz or photz)
    download_legacy_survey_data(df.copy())

    # Add extinction information to the DataFrame
    df = append_extinction_to_df(df.copy())

    # Now load the full lightcurve data, including the info from alerts
    combine_raw_source_data(df[["ztf_name"]][~df["tdescore_lc"]])
    new_df = load_raw_sources()
    for col in new_df.columns:
        if col not in df.columns:
            df[col] = new_df[col]
    full_df = combine_all_sources(df, save=False)
    return df, full_df, proc_log