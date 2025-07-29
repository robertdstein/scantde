import os
from dotenv import load_dotenv
from pathlib import Path
from scantde.paths import db_dir, sym_dir, base_html_dir, get_night_output_dir, base_output_dir, cutout_dir

import subprocess

load_dotenv()
HOST_BASE_URL = os.getenv("SERVER_BASE_URL", None)
target_base_dir = Path(HOST_BASE_URL) if HOST_BASE_URL else None


def get_rsync_command(
    source: Path,
):
    """
    Generate the rsync command to copy data from source to target.

    :param source: Source path
    :return: rsync command as a string
    """
    source_ext = source.relative_to(base_output_dir)
    target = (target_base_dir / source_ext).parent
    return f"rsync -rv {source} {target}"


def copy_files(
    source: Path,
):
    """
    Copy files from source to target using rsync.

    :param source: Source path
    :return: None
    """
    cmd = get_rsync_command(source)
    subprocess.run(cmd, shell=True)

def rsync_data(
    datestr: str,
):

    """
    Function to copy data from the local output directory to the remote server using rsync.

    :param datestr: Date string in the format YYYYMMDD
    :return: None
    """

    if target_base_dir is None:
        print("No target base directory set. Skipping rsync.")
        return

    copy_dirs = [
        db_dir,
        cutout_dir,
        get_night_output_dir(datestr),
        base_html_dir / datestr
    ]

    for copy_dir in copy_dirs:
        copy_files(copy_dir)