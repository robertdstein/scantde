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
    download_boom
)
from tdescore.combine.boom.all import parse_all_sources_boom

import numpy as np


import logging

logger = logging.getLogger(__name__)

MAX_DIST_ARCSEC = 0.9  # Max distance from nucleus in arcsec for nuclear candidates

CROSSMATCH_RADIUS = 3.0  # Distance in arcsec for PS1 crossmatch candidates
MAX_SGSCORE = 0.51 # Maximum sgscore1 value for stellar candidates

def apply_algorithmic_cuts(
    df: pd.DataFrame,
    selection: str,
    proc_log: list[ProcStage],
    require_nuclear: bool = True,
    require_multidet: bool = True,
    cut_wise: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, list[ProcStage]]:
    """
    Apply algorithmic cuts to the DataFrame of candidates.

    :param df: DataFrame containing candidates
    :param selection: selection name
    :param proc_log: processing log to update
    :param require_nuclear: whether to require nuclear candidates
    :param require_multidet: whether to require multiple detections
    :param cut_wise: whether to apply WISE cuts
    :return: DataFrame with algorithmic cuts applied
    """

    logger.info(
        f"Starting with {len(df)} sources, including {sum(df['is_tde'])} TDE alerts")
    logger.info(f"These TDEs are: {set(df[df['is_tde']]['name'].to_list())}")

    proc_log = update_processing_log(proc_log, "Initial", df)

    # Deduplicate
    logger.info("Deduplicating sources")

    new = []

    for name in tqdm(set(df["name"])):
        mask = df["name"] == name
        df_cut = df[mask].sort_values(by="jd")
        new.append(df_cut.iloc[0])

    df = pd.DataFrame(new)
    df = df.sort_values(by=["is_tde", "name"], ascending=[False, False])
    df.reset_index(drop=True, inplace=True)

    logger.info(f"Have {len(df)} unique sources, including {sum(df['is_tde'])} TDEs")

    proc_log = update_processing_log(proc_log, "De-duplicated", df)

    # Remove stars
    mask = (df["sgscore1"] < MAX_SGSCORE) | (df["sgscore1"] == -999.0) | (
                df["distpsnr1"] > CROSSMATCH_RADIUS)
    df = df[mask].copy()
    logger.info(
        f"Applying sgscore cut, leaving {len(df)} sources including {sum(df['is_tde'])} TDEs")
    proc_log = update_processing_log(
        proc_log, "Algorithmic cuts - sgscore", df
    )
    if len(df) == 0:
        raise NoSourcesError("No sources left after cut")

    # Remove galactic sources
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
        # Remove sources which are not nuclear
        mask = df["distpsnr1"] < MAX_DIST_ARCSEC

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=selection,
            stage="Algorithmic cuts - nuclear distance"
        )

        logger.info(f"Applying nuclear distance cut, leaving {len(df)} sources")

    # Remove bright hosts (gaia)
    mask = (df["neargaiabright"] > 5.) | (df["neargaiabright"] < -0.0)

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic cuts - neargaiabright"
    )

    logger.info(
        f"Applying neargaiabright cut, leaving {len(df)} sources"
    )

    # Download fast crossmatch data (no WISE)
    logger.info("Downloading alert data")
    download_boom(df.copy())

    logger.info("Combining fast crossmatch sources")
    full_df = parse_all_sources_boom(df.copy())

    # VSX distance cut
    vsx_mask = ~(full_df["VSX_distance_arcsec"] < 1.0)

    # Gaia cuts
    gaia_mask = ~((full_df["gaia_distance_arcsec"] < 1.0) & (
        (full_df["gaia_aplx"] > 5.0)
        | (full_df["gaia_apmra"] > 5.0)
        | (full_df["gaia_apmdec"] > 5.0)
    ))

    # Milliquas cuts
    milliquas_mask = ~full_df["has_milliquas"]

    # WISE cuts
    if cut_wise:
        wise_mask = ~(
                (full_df["catwise_w1_m_w2"] > 0.7)
                & (full_df["catwise_distance_arcsec"] < 2.0)
                & (full_df["distpsnr1"] < 0.5)
        )
    else:
        wise_mask = np.ones(len(full_df), dtype=bool)

    # Combine all masks
    mask = vsx_mask & gaia_mask & milliquas_mask & wise_mask

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="Algorithmic Cuts"
    )

    if require_multidet:
        full_df = parse_all_sources_boom(df.copy())
        # Remove sources with 1 detection
        mask = (full_df["ndethist"] > 3) & (full_df["ndetfilters"] > 1)

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=selection,
            stage="ndethist > 3 & ndetfilters > 1", export_db=False
        )

        if len(df) == 0:
            raise NoSourcesError("No sources left after ndethist cut")
    
    return df, full_df, proc_log