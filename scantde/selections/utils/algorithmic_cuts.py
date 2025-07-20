import pandas as pd
from scantde.log import update_processing_log, update_source_list
from scantde.errors import NoSourcesError
from tqdm import tqdm
from astropy.coordinates import SkyCoord
from scantde.selections.utils.crossmatch import download_crossmatch_fast

from scantde.log.model import ProcStage


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
)

import numpy as np


import logging

logger = logging.getLogger(__name__)

MAX_DIST_ARCSEC = 0.9  # Max distance from nucleus in arcsec for nuclear candidates

CROSSMATCH_RADIUS = 3.0  # Distance in arcsec for crossmatch candidates

def apply_algorithmic_cuts(
    df: pd.DataFrame,
    selection: str,
    proc_log: list[ProcStage],
    require_nuclear: bool = True,
    cut_wise: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, list[ProcStage]]:
    """
    Apply algorithmic cuts to the DataFrame of candidates.

    :param df: DataFrame containing candidates
    :param selection: selection name
    :param proc_log: processing log to update
    :param require_nuclear: whether to require nuclear candidates
    :param cut_wise: whether to apply WISE cuts
    :return: DataFrame with algorithmic cuts applied
    """

    logger.info(
        f"Starting with {len(df)} sources, including {sum(df['is_tde'])} TDE alerts")
    logger.info(f"These TDEs are: {set(df[df['is_tde']]['ztf_name'].to_list())}")

    proc_log = update_processing_log(proc_log, "Initial", df)

    max_sgscore = 0.5

    mask = (df["sgscore1"] < max_sgscore) | (df["sgscore1"] == -999.0) | (df["distpsnr1"] > CROSSMATCH_RADIUS)
    df = df[mask].copy()

    logger.info(
        f"Applying sgscore cut, leaving {len(df)} sources including {sum(df['is_tde'])} TDEs")

    proc_log = update_processing_log(
        proc_log, "Algorithmic cuts - sgscore", df
    )

    if len(df) == 0:
        raise NoSourcesError("No sources left after cut")

    # Deduplicate

    logger.info("Deduplicating sources")

    new = []

    for name in tqdm(set(df["ztf_name"])):
        mask = df["ztf_name"] == name
        df_cut = df[mask].sort_values(by="jd")
        new.append(df_cut.iloc[0])

    df = pd.DataFrame(new)
    df = df.sort_values(by=["is_tde", "ztf_name"], ascending=[False, False])
    df.reset_index(drop=True, inplace=True)

    logger.info(f"Have {len(df)} unique sources, including {sum(df['is_tde'])} TDEs")

    proc_log = update_processing_log(proc_log, "De-duplicated", df)

    c = SkyCoord(ra=df["ra"].values, dec=df["dec"].values, unit="deg")
    df["gal_b"] = c.galactic.b.deg

    min_gal_b = 10

    mask = (df["gal_b"] < -min_gal_b) | (df["gal_b"] > min_gal_b)

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic cuts - Galactic latitude", export_db=False
    )

    logger.info(
        f"Applying Galactic latitude cut (|b| > {min_gal_b}), "
        f"leaving {len(df)} sources"
    )

    if require_nuclear:

        mask = df["distpsnr1"] < MAX_DIST_ARCSEC

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=selection,
            stage="Algorithmic cuts - nuclear distance"
        )

        logger.info(f"Applying nuclear distance cut, leaving {len(df)} sources")

    mask = np.ones(len(df), dtype=bool)

    for column in ["sgmag1", "srmag1", "simag1", "szmag1"]:
        mask &= (df[column] > 12.) | (df[column] == -999.)

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic cuts - bright host (stellar)"
    )

    logger.info(
        f"Applying bright host (stellar) cut, leaving {len(df)} sources"
    )

    mask = (df["neargaiabright"] > 5.) | (df["neargaiabright"] < -0.0)

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic cuts - neargaiabright"
    )

    logger.info(
        f"Applying neargaiabright cut, leaving {len(df)} sources"
    )

    # Uses fast crossmatch data (no WISE)

    logger.info("Downloading fast crossmatch data")
    download_crossmatch_fast(df.copy())
    logger.info("Combining fast crossmatch sources")
    full_df = combine_all_sources(df.copy(), save=False)
    mask = (full_df["gaia_aplx"] < 3.0) & ~full_df["has_milliquas"]

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic crossmatch cuts - fast"
    )

    # Apply cuts which includes WISE data
    logger.info("Downloading WISE data")
    download_all(df.copy(), include_optional=False)

    logger.info("Combining all crossmatch data")
    full_df = combine_all_sources(df.copy(), save=False)

    if cut_wise:
        mask = (full_df["catwise_w1_m_w2"] > 0.7)
        df, proc_log = update_source_list(
            df, proc_log, ~mask, selection=selection,
            stage="CatWISE cuts"
        )
    
    return df, full_df, proc_log