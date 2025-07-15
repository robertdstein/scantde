"""
Export sources to SkyPortal
"""

import logging

from sklearn.metrics import classification_report
from tqdm import tqdm
import pandas as pd

from scantde.utils.skyportal.client import SkyportalClient
from tdescore.download.legacy_survey import default_catalog

logger = logging.getLogger(__name__)

def download_from_skyportal(sources: pd.DataFrame):
    """
    Save sources to a file

    :param sources: list of source names
    :group_id: group id
    :return: None
    """

    client = SkyportalClient()
    client.set_up_session()

    logger.info("Importing info from SkyPortal")

    sky_dicts = []

    sources.reset_index(inplace=True, drop=True)

    for i, row in tqdm(sources.iterrows(), total=len(sources)):

        new = {}

        try:

            response = client.api(
                "get",
                endpoint=f"sources/{row['ztf_name']}",
            )

            if not response.json()["status"] == "success":
                logger.debug(
                    f"Failed to save Source {row['ztf_name']} "
                    f"on SkyPortal with error: {response.json()}"
                )

            data = response.json().get("data")

            for key in ["redshift", "tns_name"]:
                new[f"skyportal_{key}"] = data.get(key)

            classifications = [x.get("classification") for x in data.get("classifications", [])]

            new["skyportal_class"] = "/".join(set(classifications)) if classifications else None


        except ConnectionError:
            logger.info(f"Failed to load Source {row['ztf_name']} on SkyPortal")
            continue

        finally:
            sky_dicts.append(new)

    sky_df = pd.DataFrame(
        sky_dicts,
        columns=["skyportal_redshift", "skyportal_tns_name", "skyportal_class"]
    )
    for col in sky_df.columns:
        sources[col] = sky_df[col]

    # sources = pd.concat([sources.reset_index(drop=True), sky_df], axis=1)
    return sources
