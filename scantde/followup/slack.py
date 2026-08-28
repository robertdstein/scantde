import pandas as pd
from tabulate import tabulate
from scantde.utils.slack import SLACK_TOKEN
from slack_sdk import WebClient
import logging

logger = logging.getLogger(__name__)

FRITZ_URL = "https://fritz.science/source/{}"

BASE_COLS = ["name", "age", "magpsf", "peak_mag", "zphot", "zorigin", "tdescore", "selection", "has_spec?"]

def get_slack_blocks(df: pd.DataFrame, columns: list[str] | None = None) -> list[dict]:
    """
    Returns a list of Slack blocks for a given DataFrame and columns.

    :param df: DataFrame to convert to Slack blocks
    :param columns: Columns to include in the Slack blocks. If None, defaults to BASE_COLS.
    :return: Nested list of Slack blocks
    """
    if columns is None:
        columns = BASE_COLS
    sub = df[list(columns)]
    sub = sub.astype(object).where(sub.notna(), None)  # so missingval catches NaN
    table = tabulate(
        sub, headers="keys", showindex=False, tablefmt="plain",
        floatfmt=".2f", missingval="-",
    )
    header, *lines = table.splitlines()

    elements = [{"type": "text", "text": header}]
    for line, name in zip(lines, df["name"].astype(str)):
        start = line.find(name)
        if start == -1:
            elements.append({"type": "text", "text": "\n" + line})
            continue
        elements.append({"type": "text", "text": "\n" + line[:start]})
        elements.append(
            {"type": "link", "text": name, "url": FRITZ_URL.format(name)})
        rest = line[start + len(name):]
        if rest:
            elements.append({"type": "text", "text": rest})

    return [{"type": "rich_text", "elements": [
        {"type": "rich_text_preformatted", "border": 0, "elements": elements}]}]

def send_table_to_slack(df, slack_channel: str, columns: list[str] | None = None):
    """
    Send a DataFrame as a table to Slack.

    :param df: DataFrame to send
    :param slack_channel: Slack channel to send the message to
    :param columns: Columns to include in the Slack message. If None, defaults to BASE_COLS.
    """
    blocks = get_slack_blocks(df, columns=columns)
    if SLACK_TOKEN is None:
        logger.warning("No slack token found, skipping sending slack message")
        return

    client = WebClient(token=SLACK_TOKEN)
    client.chat_postMessage(
        channel=slack_channel,
        username="tdescore messenger",
        text="tdescore candidate table",  # notification fallback, no links
        blocks=blocks
    )
