import logging

import pandas as pd
from tdescore.download.gaia import download_gaia_data
from tdescore.download.mast import download_panstarrs_data
from tdescore.download.kowalski import download_ps1strm_data

logger = logging.getLogger(__name__)

def download_crossmatch_fast(source_table: pd.DataFrame):
    """
    Function to download crossmatch data from external catalogues
    """
    logger.info("Downloading PS1STRM data")
    download_ps1strm_data(source_table)
    logger.info("Downloading Gaia data")
    download_gaia_data(source_table)
    logger.info("Downloading PanSTARRS data")
    download_panstarrs_data(source_table)