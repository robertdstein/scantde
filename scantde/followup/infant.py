import pandas as pd
from scantde.utils.slack import send_slack_message
from scantde.followup.slack import send_table_to_slack
from scantde.utils.skyportal import batch_check_spec
from scantde.io import load_combined
from scantde.followup.slack import BASE_COLS

MAX_REDSHIFT = 0.05
MAX_AGE = 30.0

AUTO_MAX_AGE = 14.0
AUTO_MIN_SCORE = 0.0

INFANT_COLS = BASE_COLS + ["infant_auto?"]


def apply_infant_cut(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cuts to the follow-up DataFrame to select infant TDEs

    :param df: DataFrame of sources
    :return: Cut DataFrame of sources that are likely infant TDEs
    """
    mask = (
        (df["zspec"] > 0.00)
        & (df["zspec"] < MAX_REDSHIFT)
        & pd.isnull(df["skyportal_class"])
        & (df["age"] < MAX_AGE)
    )
    df = df[mask].reset_index(drop=True)
    df = batch_check_spec(df)
    df.sort_values(by="age", ascending=True, inplace=True)

    mask = (
        (df["age"] < AUTO_MAX_AGE)
        & (~df["has_spec?"])
        & (df["tdescore"] > AUTO_MIN_SCORE)
    )
    df["infant_auto?"] = mask

    return df


def infant_assignment(datestr: str, slack_channel: str, lookback_days: int = 1):
    """
    Assign follow-up to unclassified infant sources
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
    df = apply_infant_cut(df)
    if len(df) == 0:
        send_slack_message(
            f"No infant targets for {datestr} ",
            slack_channel=slack_channel
        )
        return

    send_slack_message(
        f"Summary of unclassified transients with z<{MAX_REDSHIFT} "
        f"as of {datestr} (lookback days {lookback_days}): \n \n ",
        slack_channel=slack_channel
    )
    send_table_to_slack(df, slack_channel=slack_channel, columns=INFANT_COLS)