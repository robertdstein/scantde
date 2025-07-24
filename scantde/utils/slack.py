from pathlib import Path

import argparse
from scantde.utils import get_current_datestr
import time
import logging
import datetime
import subprocess
from slack_sdk import WebClient
from dotenv import load_dotenv
import os
from pathlib import Path
from scantde.utils import get_current_datestr

load_dotenv()

logger = logging.getLogger(__name__)

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
PUBLIC_URL = os.getenv('PUBLIC_URL', "http://127.0.0.1:5000")


def publish(
    datestr: str,
    selection: str = "tdescore",
    slack_channel: str = "scanning-ztfo4",
    url_ext: str = "lookback_days=1&hide_junk=on&mode=all",
):

    if not datestr == get_current_datestr():
        logger.info(f"Old date {datestr} provided, skipping slack publishing.")

    base_url = f"search_by_date?selection={selection}&date={datestr}&{url_ext}"
    url = Path(PUBLIC_URL) / base_url

    print(url)
    # print(f"Publishing to {url}")
    #
    # raise


    # if args.slack:
    #     if SLACK_TOKEN is None:
    #         print("No slack token found, skipping sending slack message")
    #         return
    #
    #     msg = f"Today's ({datestr}) tdescore scanning link: {public_page}"
    #
    #     client = WebClient(token=SLACK_TOKEN)
    #     client.chat_postMessage(
    #         channel="scanning-ztfo4",
    #         text=msg, username="tdescore messenger"
    #     )
    #     print(f"Sent slack message: {msg}")
    #
    #     infant_page = str(public_page).replace(TDESCORE_HTML_NAME, INFANT_HTML_NAME)
    #
    #     # Send infant page to slack
    #     msg = f"Today's ({datestr}) infant tdescore scanning link: {infant_page}"
    #     client = WebClient(token=SLACK_TOKEN)
    #     client.chat_postMessage(
    #         channel="scanning-ztfo4",
    #         text=msg, username="tdescore messenger"
    #     )
    #     print(f"Sent slack message: {msg}")





