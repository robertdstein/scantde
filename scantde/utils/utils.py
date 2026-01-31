import datetime
from pytz import timezone
from scantde.utils.skyportal import SkyportalClient, NoCredentialsError
import logging

logger = logging.getLogger(__name__)


def get_current_datestr():
    """
    Get the current date string

    :return: str Current date string
    """
    now_utc = datetime.datetime.now(timezone("UTC"))
    dtformat = "%Y%m%d %H:%M:%S %Z%z"
    datestr = now_utc.strftime(dtformat)[:8]
    return datestr


def get_known_tdes() -> list[str]:
    """
    Get the known TDES

    :return: list Known TDES
    """

    sources = []

    try:
        client = SkyportalClient()
        client.set_up_session()

        response = client.api(
            "get",
            endpoint=f"/api/sources",
            data={
                "classifications": ["Sitewide Taxonomy: Tidal Disruption Event"],
                "numPerPage": 500
            }
        )

        response.raise_for_status()
        sources = [x["id"] for x in response.json()["data"]["sources"]]

        n_matches = response.json()["data"]["totalMatches"]

        logger.debug(f"Found {len(sources)} TDEs on Skyportal, expected {n_matches}")

        assert len(sources) == n_matches

        if len(sources) == 0:
            logger.warning("No Skyportal TDEs found")
            return []

    except ConnectionError:
        logger.warning("Connection error, returning empty list")

    except NoCredentialsError:
        pass

    return sources
