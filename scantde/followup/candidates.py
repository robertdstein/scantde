"""
General CLI for summarising candidates
"""
import argparse
from datetime import datetime, timezone
from scantde.io import load_combined
from scantde.utils.skyportal import batch_check_spec
from scantde.utils import send_slack_message
from scantde.followup.cuts import apply_base_spec_cuts
from scantde.followup.slack import send_table_to_slack

def get_candidate_summary(
        datestr: str, lookback_days: int = 7, slack_channel="tdescore-followup"
):
    """
    Post a summary of unclassified candidates to Slack, split into rising and fading.

    :param datestr: Date string in the format YYYYMMDD for which to summarize candidates
    :param lookback_days: Days to look back for candidates (default is 7)
    :param slack_channel: Slack channel to post  to (default is "tdescore-followup")
    :return: None
    """
    df = load_combined(
        datestr=datestr,
        selections=["tdescore", "tdescore_offnuclear"],
        lookback_days=lookback_days
    )
    df["fading?"] = df["magpsf"] > df["peak_mag"]

    df = apply_base_spec_cuts(df)
    df = batch_check_spec(df)
    df.sort_values(by="peak_mag", inplace=True)

    if df.empty:
        send_slack_message(
            f"No unclassified candidates found as of {datestr}, "
            f"with a lookback time of {lookback_days} days.",
            slack_channel=slack_channel
        )
        return

    mask = df["fading?"]

    send_slack_message(
        f"A summary of unclassified candidates as of {datestr}, "
        f"with a lookback time of {lookback_days} days \n \n",
        slack_channel=slack_channel
    )
    if not mask.all():
        send_slack_message(
            f"Rising:", slack_channel=slack_channel
        )
        send_table_to_slack(df[~mask], slack_channel=slack_channel)
    if mask.sum() > 0:
        send_slack_message(
            f"Fading:", slack_channel=slack_channel
        )
        send_table_to_slack(df[mask], slack_channel=slack_channel)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Post a summary of unclassified tdescore candidates to Slack, "
                    "split into rising and fading."
    )
    parser.add_argument(
        "datestr",
        nargs="?",
        default=datetime.now(timezone.utc).strftime("%Y%m%d"),
        help="date to summarise, YYYYMMDD (default: today in UTC)",
    )
    parser.add_argument(
        "-l", "--lookback-days",
        type=int, default=7,
        help="days to look back for candidates (default: %(default)s)",
    )
    parser.add_argument(
        "-c", "--slack-channel",
        default="tdescore-followup",
        help="Slack channel to post to (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    if args.lookback_days < 1:
        parser.error("--lookback-days must be at least 1")

    get_candidate_summary(args.datestr, args.lookback_days, args.slack_channel)


if __name__ == "__main__":
    main()

