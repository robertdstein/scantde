import pandas as pd

from scantde.paths import cutout_dir
from ztfquery.utils import stamps
import matplotlib.pyplot as plt
import numpy as np
from requests.exceptions import HTTPError
import requests
from tqdm import tqdm

import io
from PIL import Image, UnidentifiedImageError

import logging

logger = logging.getLogger(__name__)


ps1_dir = cutout_dir / "ps1"
ps1_dir.mkdir(parents=True, exist_ok=True)

legacy_survey_dir = cutout_dir / "legacy_survey"
legacy_survey_dir.mkdir(parents=True, exist_ok=True)

def get_cutout_path(
    source_name: str,
    cutout_type: str = "ps1",
):
    """
    Get the path for a cutout image of a source.

    :param source_name: Name of the source
    :param cutout_type: Type of cutout image, either "ps1" or "legacy_survey"
    :return: Path to the cutout image
    """
    if cutout_type == "ps1":
        sub_dir = ps1_dir
    elif cutout_type == "legacy_survey":
        sub_dir = legacy_survey_dir
    else:
        logger.error(f"Unknown cutout type: {cutout_type}")
        raise ValueError(f"Unknown cutout type: {cutout_type}")
    return sub_dir / f"{source_name}.png"



def create_ps1_cutout(
    source: pd.Series,
):
    """
    Create a PS1 cutout for a given source.

    :param source: Pandas Series containing source information, including 'name'
    :return: None
    """

    cutout_path = get_cutout_path(source["name"], cutout_type="ps1")

    if cutout_path.exists():
        logger.debug(f"Cutout already exists: {cutout_path}")
        return

    ra, dec = source["ra"], source["dec"]

    try:
        img = stamps.get_ps_stamp(ra, dec, size=240, color=["y", "g", "i"])
        plt.figure(figsize=(2.1, 2.1), dpi=120)
        plt.imshow(np.asarray(img))
        plt.title("PS1 (y/g/i)", fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(cutout_path, bbox_inches="tight")
        plt.close()
    except HTTPError:
        logger.info(f"{source['name']}: HTTPConnection error in PS1 cutouts")


def create_ls_cutout(
    source: pd.Series,
):
    """
    Create a legacy survey cutout for a given source.

    :param source: Pandas Series containing source information, including 'name'
    :return: None
    """

    cutout_path = get_cutout_path(source["name"], cutout_type="legacy_survey")

    if cutout_path.exists():
        logger.debug(f"Cutout already exists: {cutout_path}")
        return

    ra, dec = source["ra"], source["dec"]

    try:
        url = (f"https://www.legacysurvey.org/viewer/cutout.jpg"
               f"?ra={ra}&dec={dec}&zoom=16")
        r = requests.get(url)
        plt.figure(figsize=(2.1, 2.1), dpi=120)
        plt.imshow(Image.open(io.BytesIO(r.content)))
        plt.title("LegSurv", fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(cutout_path, bbox_inches="tight")
        plt.close()
    except HTTPError:
        logger.info(f"{source['name']}: HTTPConnection error in LS cutouts")
    except UnidentifiedImageError:
        logger.warning(f"{source['name']}: UnidentifiedImageError in LS cutouts")
        cutout_path.unlink(missing_ok=True)


def create_cutout(
    source: pd.Series,
):
    """
    Generate cutouts for a given source from PS1 and Legacy Survey.

    :param source: Source row
    :return: None
    """
    create_ps1_cutout(source)
    create_ls_cutout(source)


def batch_create_cutouts(
    df: pd.DataFrame,
):
    """
    Batch create cutouts for a DataFrame of sources.

    :param df: DataFrame containing source information
    :return: None
    """
    for _, source in tqdm(df.iterrows(), total=len(df)):
        create_cutout(source)
        logger.debug(f"Cutouts created for {source['name']}")
