"""
Export sources to SkyPortal
"""

import logging
from tqdm import tqdm
import pandas as pd

from scantde.utils.skyportal.client import SkyportalClient
from urllib3.exceptions import MaxRetryError
from requests.exceptions import RetryError

logger = logging.getLogger(__name__)

def export_to_skyportal(sources: pd.DataFrame, group_ids: list[int] | None = None):
    """
    Save sources to a file

    :param sources: list of source names
    :param group_ids: list of group ids (default [1679])
    :return: None
    """

    client = SkyportalClient()
    client.set_up_session()

    if group_ids is None:
        group_ids = [1679]

    logger.info(f"Exporting sources to SkyPortal groups {group_ids}")

    for i, row in tqdm(sources.iterrows(), total=len(sources)):

        if row["tdescore"] < 0.01:
            logger.debug(
                f"Skipping Source {row['ztf_name']} with TDEScore {row['tdescore']}"
            )
            continue

        # Save source to SkyPortal
        try:
            # check if source exists on SkyPortal

            response = client.api(
                "head",
                endpoint=f"sources/{row['ztf_name']}",
            )

            # If it does not exist, create it
            if not response.ok:
                response = client.api(
                    "post",
                    endpoint=f"brokers/1/alerts/{row['ztf_name']}/save",
                    data={"group_ids": group_ids},
                )
                if not response.json()["status"] == "success":
                    logger.info(
                        f"Failed to create Source {row['ztf_name']} "
                        f"on SkyPortal with error: {response.json()}"
                    )

            # Check saved groups
            response = client.api(
                "get",
                endpoint=f"sources/{row['ztf_name']}/groups",
            )

            if response.json()["status"] == "success":
                existing_group_ids = [int(x["id"]) for x in response.json()["data"]]
            else:
                existing_group_ids = []

            missing_ids = [
                int(group_id) for group_id in group_ids
                if int(group_id) not in existing_group_ids
            ]

            # If not in right groups, save it to the right groups
            if len(missing_ids) > 0:
                response = client.api(
                    "post",
                    endpoint=f"source_groups",
                    data={"objId": row['ztf_name'], "inviteGroupIds": missing_ids},
                )

                if not response.json()["status"] == "success":
                    logger.error(
                        f"Failed to save Source {row['ztf_name']} "
                        f"to group {missing_ids} "
                        f"on SkyPortal with error: {response.json()}"
                    )
            else:
                logger.debug(f"Source {row['ztf_name']} already in groups {group_ids}")

        except (ConnectionError, RetryError, MaxRetryError) as exc:
            logger.error(f"Failed for {row['ztf_name']} on SkyPortal with error: {exc}")
            continue

    logger.info("Exporting redshift data to SkyPortal")

    key = f"zspec"

    if key not in sources.columns:
        logger.warning(f"Redshift data key '{key}' not found")
        return

    for i, row in tqdm(sources.iterrows(), total=len(sources)):

        specz = row["zspec"]

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

                # res = response.json()["data"]["redshift"]
                #
                # if res is None:
                #     # Export redshift data to SkyPortal
                #     response = client.api(
                #         "patch",
                #         endpoint=f"sources/{row['ztf_name']}",
                #         data={
                #             "redshift": float(f"{float(specz):.2f}"),
                #             "redshift_origin": row["zorigin"],
                #         },
                #     )
                #     if not response.json()["status"] == "success":
                #         logger.error(
                #             f"Failed to save redshift {row['ztf_name']} "
                #             f"on SkyPortal with error: {response.json()}"
                #         )
                #     else:
                #         logger.info(
                #             f"Saved redshift {row['ztf_name']} "
                #             f"on SkyPortal with value {specz}"
                #         )

            except (ConnectionError, RetryError, MaxRetryError):
                logger.error(f"Failed to save redshift {row['ztf_name']} on SkyPortal")
                continue