"""
Module for automated SOAR follow-up of TDE candidates
"""
import pandas as pd
from scantde.followup.utils import get_best_airmass
from scantde.utils.skyportal import batch_check_spec
from scantde.followup.cuts import apply_base_spec_cuts
from scantde.followup.slack import BASE_COLS
from scantde.utils.slack import send_slack_message
from scantde.followup.slack import send_table_to_slack
from scantde.io import load_combined

MAX_MAG_SOAR = 19.9
MAX_AIRMASS_SOAR = 2.0
MIN_AGE_SOAR = 0.0  # days
MIN_SCORE_SOAR = 0.1  # minimum TDEScore for SOAR follow-up

AUTO_MAG_SOAR = 19.3
AUTO_AGE_SOAR = 14.0  # days
AUTO_AIRMASS_SOAR = 2.0
AUTO_SCORE_SOAR = 0.4


SOAR_COLS = BASE_COLS + ["soar_airmass", "soar_auto"]


def check_soar_airmass(row: pd.Series) -> float:
    """
    Function to check the airmass of a source for SOAR observations.

    :param row: A row from the sources table
    :return: Airmass value (float) or NaN if the source is not observable
    """
    return get_best_airmass(row["ra"], row["dec"], site="Cerro Pachon")


def batch_check_soar_airmass(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to batch check the airmass of sources for SOAR observations.

    :param df: Table of sources
    :return: Table of sources with airmass column added
    """
    df["soar_airmass"] = df.apply(check_soar_airmass, axis=1)
    return df


def apply_soar_cuts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to apply SOAR cuts to a table of sources

    :param df: Table of sources
    :return: Table of sources after cuts
    """
    df = apply_base_spec_cuts(df)

    mask = (
        (df["magpsf"] < MAX_MAG_SOAR) &
        (df["tdescore"] > MIN_SCORE_SOAR) &
        (df["age"] > MIN_AGE_SOAR)
    )

    df = df[mask]

    df = batch_check_soar_airmass(df)

    df = df[df["soar_airmass"] < MAX_AIRMASS_SOAR]

    df = batch_check_spec(df)

    df = df[mask].reset_index(drop=True)
    df.sort_values(by=["tdescore"], ascending=False, inplace=True)

    df["soar_auto"] = (
        (df["soar_airmass"] < AUTO_AIRMASS_SOAR)
        & (df["age"] > AUTO_AGE_SOAR)
        & (df["magpsf"] < AUTO_MAG_SOAR)
        & (df["tdescore"] > AUTO_SCORE_SOAR)
        & (~df["has_spec?"])
    )

    return df


def soar_assignment(datestr: str, slack_channel: str, lookback_days: int = 1):
    """
    Assign SOAR follow-up to unclassified likely-real sources
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
    df = apply_soar_cuts(df)
    if len(df) == 0:
        send_slack_message(
            f"No valid SOAR-able targets for {datestr} ",
            slack_channel=slack_channel
        )
        return

    send_slack_message(
        f"Summary of unclassified SOAR-able transients as of {datestr} "
        f"(lookback days {lookback_days}): \n \n ",
        slack_channel=slack_channel
    )
    send_table_to_slack(df, slack_channel=slack_channel, columns=SOAR_COLS)
