"""
Get SEDm sample
"""
from astropy import units as u
import pandas as pd
from scantde.followup.cuts import apply_base_spec_cuts
from scantde.utils.skyportal import get_followup, SkyportalClient, batch_check_spec
from tqdm import tqdm
from astropy.time import Time
from scantde.utils.slack import send_slack_message
from scantde.followup.slack import send_table_to_slack
from scantde.io import load_combined

BASE_SEDM_PAYLOAD = {
    "observation_type": "IFU",
    "priority": 2.9,
}


def apply_sedm_cuts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply SEDm cuts to the follow-up DataFrame

    :param df: DataFrame of sources
    :return: List of unclassified likely-real sources
    """
    df = apply_base_spec_cuts(df)
    mask = df["magpsf"] < 18.5
    return df[mask]


def check_sedm(name) -> tuple[bool, bool]:
    """
    Check if a source has pending or completed SEDm follow-up requests

    :param name: Name of the source
    :return: List of booleans indicating if there are pending and completed SEDm follow-up requests
    """
    fdf = get_followup(name)
    if fdf.empty:
        return False, False

    sedm_request = [x["instrument"]["name"] == "SEDM" for x in fdf["allocation"]]
    fdf = fdf[sedm_request]

    spec_request = ["IFU" in x["observation_type"] for x in fdf["payload"]]
    fdf = fdf[spec_request]

    pending = (fdf["status"] == "submitted").sum() > 0
    completed = (fdf["status"] != "submitted").sum() > 0
    return pending, completed


def batch_check_sedm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check the follow-up requests for SEDm for a batch of sources

    :param df: Input DataFrame of sources
    :return: DataFrame with additional columns for SEDm follow-up status
    """
    pending = []
    completed = []
    for name in tqdm(df["name"]):
        pend, comp = check_sedm(name)
        pending.append(pend)
        completed.append(comp)
    df["has_sedm_spec?"] = completed
    df["pending_sedm?"] = pending
    return df


def get_sedm_list(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the list of sources that are suitable for SEDm follow-up

    :param df: DataFrame of sources
    :return: List of unclassified likely-real sources suitable for SEDm follow-up
    """
    df = apply_sedm_cuts(df)
    df = batch_check_sedm(df)
    df = batch_check_spec(df)
    return df

def send_target_to_sedm(name: str, allocation: int = 1038) -> bool:
    """
    Send a target to SEDm for follow-up
    """
    sedm_payload = BASE_SEDM_PAYLOAD.copy()
    sedm_payload["start_date"] = Time.now().isot
    sedm_payload["end_date"] = (Time.now() + 7. * u.day).isot

    response = SkyportalClient().api(
        "post",
        endpoint="followup_request",
        data={"obj_id": name, "allocation_id": allocation, "payload": sedm_payload},
    )
    return response.status_code == 200


def sedm_assignment(datestr: str, slack_channel: str, lookback_days: int = 1):
    """
    Assign SEDm follow-up to unclassified likely-real sources
    and send a summary to Slack

    :param datestr: Date string in YYYYMMDD format
    :param slack_channel: Slack channel to post to
    :param lookback_days: Days to look back for candidates (default is 1)
    """
    df = load_combined(
        datestr=datestr,
        selections=["tdescore", "tdescore_offnuclear"],
        lookback_days=lookback_days
    )
    df = get_sedm_list(df)
    if len(df) == 0:
        send_slack_message(
            f"No valid SEDm-able targets for {datestr} ",
            slack_channel=slack_channel
        )
        return

    spec_check = (df["has_sedm_spec?"] | df["has_spec?"]) & ~(df["pending_sedm?"])
    mask = ~(spec_check | df["pending_sedm?"])

    send_slack_message(
        f"Summary of unclassified SEDm-able transients as of {datestr} "
        f"(lookback days {lookback_days}): \n \n ",
        slack_channel=slack_channel
    )

    if mask.sum() > 0:

        passed, failed = [], []

        for i, row in df[mask].iterrows():
            name = row["name"]
            success = send_target_to_sedm(name)
            passed.append(name) if success else failed.append(name)

        if len(passed) > 0:
            send_slack_message("Newly Assigned:", slack_channel=slack_channel)
            send_table_to_slack(df[df["name"].isin(passed)],
                                slack_channel=slack_channel)
        if len(failed) > 0:
            send_slack_message("Failed to Assign:", slack_channel=slack_channel)
            send_table_to_slack(df[df["name"].isin(failed)],
                                slack_channel=slack_channel)

    if df["pending_sedm?"].sum() > 0:
        send_slack_message("Already pending:", slack_channel=slack_channel)
        send_table_to_slack(df[df["pending_sedm?"]], slack_channel=slack_channel)
    if spec_check.sum() > 0:
        send_slack_message("Already has spec:", slack_channel=slack_channel)
        send_table_to_slack(df[spec_check], slack_channel=slack_channel)



