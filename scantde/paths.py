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

db_path = base_output_dir / 'scantde.db'

base_html_dir = base_output_dir / 'html'
base_html_dir.mkdir(parents=True, exist_ok=True)

# Symlink for html
sym_dir = code_dir / "static"
if not sym_dir.exists():
    sym_dir.symlink_to(base_html_dir, target_is_directory=True)

ml_dir = code_dir / 'ml_models'
ml_dir.mkdir(exist_ok=True)


def get_night_output_dir(datestr: str) -> Path:
    """
    Get the output directory for a given date.

    :param datestr: Date string in the format 'YYYY-MM-DD'
    :return: Path to the output directory for the given date
    """
    output_dir = base_output_dir / datestr
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

# authdir = parentdir / 'auth'
#
# outputdir = parentdir_data / 'output'
#
# expdir = parentdir_data / 'exposure_history'
# datadir = parentdir_data / 'data'
# tdescoredir = parentdir_data / 'tdescore_output'

#
# base_html_dir = parentdir_data / 'mbh_html'
# htmldir = base_html_dir #/ 'nuclear'
# tdescore_html_dir = base_html_dir / 'tdescore'
#
# sourcedir = parentdir_data / "sources"
#
# sfd_dir = parentdir / 'sfddata-master/'
#
# ml_dir = parentdir_data / 'ml_models'
# ml_dir.mkdir(exist_ok=True)
#
# tdefile = datadir / "known_tde_names.dat"