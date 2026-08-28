import pandas as pd
from scantde.utils.skyportal.client import SkyportalClient
from tqdm import tqdm

def get_followup(name: str, drop_expired: bool = True) -> pd.DataFrame:
    """
    Fetch followup requests for a given source from SkyPortal

    :param name: Source name
    :param drop_expired: Drop expired followup requests (default True)
    :return: List of followup requests as a DataFrame
    """

    client = SkyportalClient()
    client.set_up_session()

    response = client.api(
        "get",
        endpoint=f"followup_request",
        data={"sourceID": name},
    )
    response.raise_for_status()
    df = pd.DataFrame(response.json()["data"]["followup_requests"])
    if drop_expired and len(df) > 0:
        df = df[~df["status"].isin(["Expired"])]
    return df


def get_spectra(name: str) -> pd.DataFrame:
    """
    Fetch spectra for a given source from SkyPortal

    :param name: Source name
    :return: List of spectra as a DataFrame
    """

    client = SkyportalClient()
    client.set_up_session()

    response = client.api(
        "get",
        endpoint=f"spectra",
        data={"objID": name, "minimalPayload": True},
    )
    response.raise_for_status()
    df = pd.DataFrame(response.json()["data"])
    return df

def batch_check_spec(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check if a batch of sources have spectra in SkyPortal

    :param df: DataFrame of sources
    :return: DataFrame with additional column indicating if each source has a spectrum
    """
    has_spec = []
    for name in tqdm(df["name"]):
        specs = get_spectra(name)
        has_spec.append(len(specs) > 0)
    df["has_spec?"] = has_spec
    return df