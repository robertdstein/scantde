"""
Module for defining paths used in the scantde package.
"""
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

# This always points to the scan_tde directory
code_dir = Path(__file__).resolve().parents[1]

_base_output_dir = os.getenv("SCANTDE_DATA_DIR")

if _base_output_dir is None:
    base_output_dir = code_dir / 'output'
    base_output_dir.mkdir(parents=True, exist_ok=True)
else:
    base_output_dir = Path(_base_output_dir).resolve()

tdescore_output_dir = base_output_dir / 'tdescore_output'
tdescore_output_dir.mkdir(parents=True, exist_ok=True)

base_html_dir = base_output_dir / 'html'
base_html_dir.mkdir(parents=True, exist_ok=True)

# Symlink for html
sym_dir = code_dir / "static"
if not sym_dir.exists():
    sym_dir.symlink_to(base_html_dir, target_is_directory=True)

# Copy images to the static directory
image_dir = code_dir / "images"
images = [x for x in image_dir.glob("*") if x.suffix in [".png", ".ico"]]
for image in images:
    target = sym_dir / image.name
    if not target.exists():
        target.symlink_to(image)

ml_dir = code_dir / 'ml_models'
ml_dir.mkdir(exist_ok=True)

cutout_dir = base_html_dir / 'cutouts'
cutout_dir.mkdir(exist_ok=True)

input_cache_dir = base_output_dir / 'input_cache'
input_cache_dir.mkdir(parents=True, exist_ok=True)

db_dir = base_output_dir / 'db'
db_dir.mkdir(parents=True, exist_ok=True)


def get_db_path(selection: str) -> Path:
    """
    Get the database path for a given selection type.

    :param selection: Selection type (e.g., 'tdescore')
    :return: Path to the database file for the given selection
    """
    return db_dir / f'scantde_{selection}.db'


def get_input_cache(datestr: str) -> Path:
    """
    Get the input cache filename for a given date.

    :param datestr: Date string in the format 'YYYYMMDD'
    :return:
    """
    output_dir = input_cache_dir / f'{datestr}'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_candidate_cache(datestr: str, selection: str) -> Path:
    """
    Get the cache filename for candidates for a given date and selection type.

    :param datestr: Date string in the format 'YYYYMMDD'
    :param selection: Selection type (e.g., 'tdescore')
    :return: Path to the cache file for candidates
    """
    cache_dir = get_input_cache(datestr)
    return cache_dir / f'/scantde_{selection}_candidates.json'


def get_night_output_dir(datestr: str) -> Path:
    """
    Get the output directory for a given date.

    :param datestr: Date string in the format 'YYYY-MM-DD'
    :return: Path to the output directory for the given date
    """
    output_dir = base_output_dir / "results" / datestr
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_log_path(datestr: str, selection: str) -> Path:
    """
    Get the log file path for a given selection type.

    :param datestr: Date string in the format 'YYYYMMDD'
    :param selection: Selection type (e.g., 'tdescore')
    :return: Path to the log file for the given selection
    """
    return get_night_output_dir(datestr) / f'scantde_{selection}_log.json'
