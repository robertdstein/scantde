import logging
from slack_sdk import WebClient
from dotenv import load_dotenv
import os
from scantde.utils import get_current_datestr

load_dotenv()

logger = logging.getLogger(__name__)

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
BASE_URL = os.getenv('BASE_PUBLIC_URL', "https://127.0.0.1:5000")
EXT = os.getenv("SERVER_EXT", None)
PUBLIC_URL = f"{os.path.join(BASE_URL, EXT)}" if EXT else BASE_URL


def send_slack_message(message: str, slack_channel: str = "ztf-scantde-o4"):
    """
    Send a message to a Slack channel.

    :param message: Message to send
    :param slack_channel: Slack channel to send the message to
    :return: None
    """
    if SLACK_TOKEN is None:
        logger.warning("No slack token found, skipping sending slack message")
        return

    client = WebClient(token=SLACK_TOKEN)
    client.chat_postMessage(
        channel=slack_channel,
        text=message,
        username="tdescore messenger"
    )


def send_to_slack(
    datestr: str,
    selection: str = "tdescore",
    slack_channel: str = "ztf-scantde-o4",
    url_ext: str = "lookback_days=1&min_score=0.01&hide_junk=on&mode=all",
):

    alt_datestr = f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}"

    base_url = f"search_by_date?selection={selection}&date={alt_datestr}&{url_ext}"
    url = f"{PUBLIC_URL.rstrip('/')}/{base_url}"

    msg = f"Today's ({datestr}) tdescore scanning link: {url}"
    logger.info(msg)

    if datestr != get_current_datestr():
        logger.info(f"Skipping publishing for {datestr}, not today's date")
    else:
        send_slack_message(msg, slack_channel)



