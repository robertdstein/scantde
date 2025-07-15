from pathlib import Path
import json
import pandas as pd
import logging
from scantde.selections.tdescore.make_html import TDESCORE_HTML_DIR
from scantde.paths import get_night_output_dir

logger = logging.getLogger(__name__)


def candidates_cache_filename(datestr: str) -> Path:
    """
    Get the cache filename for a given date

    :param datestr: Date to get the cache filename for
    :return: Path Cache filename
    """
    return get_night_output_dir(datestr) / "tdescore_candidates.json"


def save_candidates(datestr: str, candidates: pd.DataFrame) -> None:
    """
    Save the candidates to a cache file

    :param datestr: Date to save the candidates for
    :param candidates: pd.DataFrame Candidates to save
    :return: None
    """
    cache_filename = candidates_cache_filename(datestr)
    candidates.to_json(cache_filename)
    logger.info(f"Saved candidates to {cache_filename}")


def load_candidates(datestr: str) -> pd.DataFrame:
    """
    Load the candidates from a cache file

    :param datestr: Date to load the candidates for
    :return: pd.DataFrame Candidates
    """
    cache_filename = candidates_cache_filename(datestr)
    if not cache_filename.exists():
        err = f"No cache file found at {cache_filename}"
        logger.error(err)
        raise FileNotFoundError(err)
    candidates = pd.read_json(cache_filename)
    logger.info(f"Loaded candidates from {cache_filename}")
    return candidates

def results_cache_filename(datestr: str) -> Path:
    """
    Get the cache filename for the results of TDEScore for a given date

    :param datestr: Date to get the cache filename for
    :return: Path Cache filename
    """
    return TDESCORE_HTML_DIR / datestr / "tdescore_results.json"

def save_results(datestr: str, result_df: pd.DataFrame) -> None:
    """
    Save the results of TDEScore to a cache file

    :param datestr: Date to save the results for
    :param result_df: pd.DataFrame Results to save
    :return: None
    """
    cache_filename = results_cache_filename(datestr)
    cache_filename.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_json(cache_filename)
    logger.info(f"Saved TDEScore results to {cache_filename}")


def load_results(datestr: str) -> pd.DataFrame:
    """
    Load the results of TDEScore from a cache file

    :param datestr: Date to load the results for
    :return: pd.DataFrame Results
    """
    cache_filename = results_cache_filename(datestr)
    if not cache_filename.exists():
        err = f"No cache file found at {cache_filename}"
        logger.error(err)
        raise FileNotFoundError(err)
    result_df = pd.read_json(cache_filename)
    logger.info(f"Loaded TDEScore results from {cache_filename}")
    return result_df


