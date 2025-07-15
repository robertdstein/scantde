"""
Export sources to SkyPortal
"""

import logging
from tqdm import tqdm
import pandas as pd

from scantde.utils.skyportal.client import SkyportalClient
from tdescore.download.legacy_survey import default_catalog

logger = logging.getLogger(__name__)

def export_to_skyportal(sources: pd.DataFrame, group_id: int = 1679):
    """
    Save sources to a file

    :param sources: list of source names
    :group_id: group id
    :return: None
    """

    client = SkyportalClient()
    client.set_up_session()

    group_ids = [int(group_id)]

    logger.info("Exporting sources to SkyPortal")

    for i, row in tqdm(sources.iterrows(), total=len(sources)):

        try:

            response = client.api(
                "post",
                endpoint=f"alerts/{row['ztf_name']}",
                data={"group_ids": group_ids}
            )

            if not response.json()["status"] == "success":
                logger.info(
                    f"Failed to save Source {row['ztf_name']} "
                    f"on SkyPortal with error: {response.json()}"
                )

        except ConnectionError:
            logger.info(f"Failed to save Source {row['ztf_name']} on SkyPortal")
            continue

    logger.info("Exporting redshift data to SkyPortal")

    key = f"{default_catalog}_z_spec"

    if key not in sources.columns:
        logger.warning(f"Redshift data key '{key}' not found")
        return

    for i, row in tqdm(sources.iterrows(), total=len(sources)):

        specz = row[f"{default_catalog}_z_spec"]

        if specz > 0:

            try:
                response = client.api(
                    "get",
                    endpoint=f"sources/{row['ztf_name']}",
                )

                if not response.json()["status"] == "success":
                    logger.error(
                        f"Failed to load redshift {row['ztf_name']} "
                        f"on SkyPortal with error: {response.json()}"
                    )
                    continue

                res = response.json()["data"]["redshift"]

                if res is None:

                    # Export redshift data to SkyPortal
                    response = client.api(
                        "patch",
                        endpoint=f"sources/{row['ztf_name']}",
                        data={
                            "redshift": specz,
                            "redshift_origin": f"{default_catalog} (specz)",
                        },
                    )
                    if not response.json()["status"] == "success":
                        logger.error(
                            f"Failed to save redshift {row['ztf_name']} "
                            f"on SkyPortal with error: {response.json()}"
                        )
                    else:
                        logger.info(
                            f"Saved redshift {row['ztf_name']} "
                            f"on SkyPortal with value {specz}"
                        )

            except ConnectionError:
                logger.error(f"Failed to save redshift {row['ztf_name']} on SkyPortal")
                continue