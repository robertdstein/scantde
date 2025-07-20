from pathlib import Path
import pandas as pd
import logging
from scantde.html.make_html import TDESCORE_HTML_DIR
from scantde.paths import get_night_output_dir

logger = logging.getLogger(__name__)


def candidates_cache_filename(datestr: str, selection: str) -> Path:
    """
    Get the cache filename for a given date

    :param datestr: Date to get the cache filename for
    :param selection: Selection type (e.g., 'tdescore')
    :return: Path Cache filename
    """
    return get_night_output_dir(datestr) / f"scantde_{selection}_candidates.json"


def save_candidates(datestr: str, selection: str, candidates: pd.DataFrame) -> None:
    """
    Save the candidates to a cache file

    :param datestr: Date to save the candidates for
    :param selection: Selection type (e.g., 'tdescore')
    :param candidates: pd.DataFrame Candidates to save
    :return: None
    """
    cache_filename = candidates_cache_filename(datestr, selection)
    candidates.to_json(cache_filename)
    logger.info(f"Saved candidates to {cache_filename}")


def load_candidates(datestr: str, selection: str) -> pd.DataFrame:
    """
    Load the candidates from a cache file

    :param datestr: Date to load the candidates for
    :param selection: Selection type (e.g., 'tdescore')
    :return: pd.DataFrame Candidates
    """
    cache_filename = candidates_cache_filename(datestr, selection)
    if not cache_filename.exists():
        err = f"No cache file found at {cache_filename}"
        logger.error(err)
        raise FileNotFoundError(err)
    candidates = pd.read_json(cache_filename)
    logger.info(f"Loaded candidates from {cache_filename}")
    return candidates


def results_cache_filename(datestr: str, selection: str) -> Path:
    """
    Get the cache filename for the results of TDEScore for a given date

    :param datestr: Date to get the cache filename for
    :return: Path Cache filename
    """
    return TDESCORE_HTML_DIR / datestr / f"scantde_{selection}_results.json"


def save_results(datestr: str, selection: str, result_df: pd.DataFrame) -> None:
    """
    Save the results of TDEScore to a cache file

    :param datestr: Date to save the results for
    :param result_df: pd.DataFrame Results to save
    :return: None
    """
    cache_filename = results_cache_filename(datestr, selection)
    cache_filename.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_json(cache_filename)
    logger.info(f"Saved scantde results to {cache_filename}")


def load_results(datestr: str, selection: str) -> pd.DataFrame:
    """
    Load the results of TDEScore from a cache file

    :param datestr: Date to load the results for
    :return: pd.DataFrame Results
    """
    cache_filename = results_cache_filename(datestr, selection)
    if not cache_filename.exists():
        err = f"No cache file found at {cache_filename}"
        logger.error(err)
        raise FileNotFoundError(err)
    result_df = pd.read_json(cache_filename)
    logger.info(f"Loaded scantde results from {cache_filename}")
    return result_df


