import logging
from slack_sdk import WebClient
from dotenv import load_dotenv
import os
from pathlib import Path
from scantde.utils import get_current_datestr

load_dotenv()

logger = logging.getLogger(__name__)

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
PUBLIC_URL = os.getenv('PUBLIC_URL', "http://127.0.0.1:5000")


def send_to_slack(
    datestr: str,
    selection: str = "tdescore",
    slack_channel: str = "ztf-scantde-o4",
    url_ext: str = "lookback_days=1&min_score=0.01&hide_junk=on&mode=all",
):

    alt_datestr = f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}"

    base_url = f"search_by_date?selection={selection}&date={alt_datestr}&{url_ext}"
    url = Path(PUBLIC_URL) / base_url

    msg = f"Today's ({datestr}) tdescore scanning link: {url}"
    logger.info(msg)

    if datestr != get_current_datestr():
        logger.info(f"Skipping publishing for {datestr}, not today's date")
    else:
        if SLACK_TOKEN is None:
            logger.info("No slack token found, skipping sending slack message")
            return

        client = WebClient(token=SLACK_TOKEN)
        client.chat_postMessage(
            channel=slack_channel,
            text=msg, username="tdescore messenger"
        )



