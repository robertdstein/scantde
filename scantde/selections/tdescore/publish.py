from pathlib import Path

import argparse
from scantde.utils import get_current_datestr
import time
import logging
import datetime
import subprocess
from slack_sdk import WebClient
from scantde.html.make_html import TDESCORE_HTML_NAME, INFANT_HTML_NAME, TDESCORE_HTML_DIR

logger = logging.getLogger(__name__)


def publish():
    logger.setLevel(logging.INFO)
    logging.getLogger("scantde").setLevel(logging.INFO)

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-n", "--night", "--datestr",
        dest="datestr",
        type=str, help="Date to run the integration for", required=False, default=None
    )
    argparser.add_argument(
        "-o", "--outdir", required=False, help="Subdirectory to send to public_html", default="tdescore"
    )
    argparser.add_argument(
        "--slack", help="Publish to slack", default=False, action="store_true"
    )
    args = argparser.parse_args()

    public_html_dir = Path.home() / "public_html"

    if not public_html_dir.exists():
        raise FileNotFoundError(f"Output directory {public_html_dir} does not exist")

    datestr = args.datestr
    if datestr is None:
        datestr = get_current_datestr()

    print(f"Publishing for {datestr}")

    page_ext = Path(datestr) / TDESCORE_HTML_NAME

    input_page = TDESCORE_HTML_DIR / datestr / TDESCORE_HTML_NAME

    if not input_page.exists():
        n_iter = 0
        while not input_page.exists() and n_iter < 180:
            print(f"No HTML page found at {input_page} at "
                  f"{datetime.datetime.now()}, waiting for 5 minutes...")
            time.sleep(300)
            n_iter += 1

    base_output_dir = public_html_dir / args.outdir

    rsync_command = f"rsync -rt {TDESCORE_HTML_DIR}/* {base_output_dir}"

    print(f"Rsyncing:\n {rsync_command}")

    subprocess.run(rsync_command, shell=True, check=True, capture_output=True)

    output_page = public_html_dir / args.outdir / page_ext

    if not output_page.exists():
        raise FileNotFoundError(f"Output page {output_page} does not exist")

    print(f"Published to {output_page}")

    public_page = f"https://sites.astro.caltech.edu/" \
                  f"~{Path.home().name}/{Path(args.outdir) / page_ext}"

    print(f"Public page: {public_page}")

    if args.slack:
        if slack_token is None:
            print("No slack token found, skipping sending slack message")
            return

        msg = f"Today's ({datestr}) tdescore scanning link: {public_page}"

        client = WebClient(token=slack_token)
        client.chat_postMessage(
            channel="scanning-ztfo4",
            text=msg, username="tdescore messenger"
        )
        print(f"Sent slack message: {msg}")

        infant_page = str(public_page).replace(TDESCORE_HTML_NAME, INFANT_HTML_NAME)

        # Send infant page to slack
        msg = f"Today's ({datestr}) infant tdescore scanning link: {infant_page}"
        client = WebClient(token=slack_token)
        client.chat_postMessage(
            channel="scanning-ztfo4",
            text=msg, username="tdescore messenger"
        )
        print(f"Sent slack message: {msg}")





