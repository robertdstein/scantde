"""
Export sources to SkyPortal
"""

import logging

from sklearn.metrics import classification_report
from tqdm import tqdm
import pandas as pd
from pathlib import Path

from scantde.utils.skyportal.client import SkyportalClient
from tdescore.download.legacy_survey import default_catalog
from scantde.paths import get_input_cache

logger = logging.getLogger(__name__)

SKYPORTAL_DF_COLUMNS = [
    "ztf_name", "skyportal_redshift", "skyportal_tns_name", "skyportal_class"
]


def get_skyportal_path(datestr: str) -> Path:
    """
    Get the path to the SkyPortal file for a given date and selection

    :param datestr: Date string
    :return: Path to the SkyPortal file
    """
    input_cache = get_input_cache(datestr)
    return input_cache / f"skyportal_cache.json"


def download_from_skyportal(names: list[str], datestr: str):
    """
    Save sources to a file

    :param names: list of source names
    :param datestr: Date string
    :return: None
    """

    skyportal_path = get_skyportal_path(datestr)

    if skyportal_path.exists():
        old = pd.read_json(
            skyportal_path,
            orient="records",
            lines=True,
        )
    else:
        old = pd.DataFrame(columns=SKYPORTAL_DF_COLUMNS)

    client = SkyportalClient()
    client.set_up_session()

    logger.info("Importing info from SkyPortal")

    sky_dicts = []

    for name in tqdm(names):

        new = {"ztf_name": name}

        try:

            response = client.api(
                "get",
                endpoint=f"sources/{name}",
            )

            if not response.json()["status"] == "success":
                logger.debug(
                    f"Failed to save Source {name} "
                    f"on SkyPortal with error: {response.json()}"
                )

            data = response.json().get("data")

            for key in ["redshift", "tns_name"]:
                new[f"skyportal_{key}"] = data.get(key)

            classifications = [x.get("classification") for x in data.get("classifications", [])]

            new["skyportal_class"] = "/".join(set(classifications)) if classifications else None


        except ConnectionError:
            logger.info(f"Failed to load Source {name} on SkyPortal")
            continue

        finally:
            sky_dicts.append(new)

    sky_df = pd.DataFrame(
        sky_dicts,
        columns=SKYPORTAL_DF_COLUMNS
    )

    mask = ~old["ztf_name"].isin(names)

    if mask.any():
        if len(sky_df) == 0:
            sky_df = old[mask]
        else:
            sky_df = pd.concat([sky_df, old[mask]], ignore_index=True)

    sky_df.to_json(
        skyportal_path,
        orient="records",
        lines=True,
    )


def get_skyportal_data(
    sources: pd.DataFrame,
    datestr: str,
) -> pd.DataFrame:
    """
    Get SkyPortal data for a list of sources

    :param sources: DataFrame of sources
    :param datestr: Date string
    :return: DataFrame with SkyPortal data
    """

    skyportal_path = get_skyportal_path(datestr)

    if not skyportal_path.exists():
        download_from_skyportal(names=sources["name"], datestr=datestr)
    else:
        old = pd.read_json(skyportal_path, orient="records", lines=True)
        names = [x for x in sources["ztf_name"] if x not in old["ztf_name"].tolist()]
        download_from_skyportal(names, datestr=datestr)

    sky_df = pd.read_json(skyportal_path, orient="records", lines=True)
    sky_df.set_index("ztf_name", inplace=True)
    join = sources.join(sky_df, on="ztf_name", how="left")
    return join
