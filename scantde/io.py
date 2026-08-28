from pathlib import Path
import pandas as pd
import logging
import numpy as np
from scantde.paths import get_night_output_dir, base_html_dir
from scantde.log import load_processing_log, merge_processing_logs, ProcStage

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
    :param selection: Selection type (e.g., 'tdescore')
    :return: Path Cache filename
    """
    output_dir = candidates_cache_filename(datestr, selection).parent
    return output_dir / f"scantde_{selection}_results.json"


def save_results(datestr: str, selection: str, result_df: pd.DataFrame) -> None:
    """
    Save the results of TDEScore to a cache file

    :param datestr: Date to save the results for
    :param selection: Selection type (e.g., 'tdescore')
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
    :param selection: Selection type (e.g., 'tdescore')
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

def load_single_df(datestr: str, selection: str) -> pd.DataFrame:
    """
    Load a DataFrame for a given date string

    :param datestr: str date string in 'YYYYMMDD' format
    :param selection: str selection type (e.g., 'tdescore')
    :return: DataFrame of results
    """
    df = load_results(datestr, selection=selection)
    df = df.copy()
    df["datestr"] = datestr
    df["thermal_window"] = df["thermal_window"].replace({np.nan: None})
    return df


FALLBACK_COLUMNS = ["name", "tdescore", "tdescore_best", "is_junk", "magpsf", "is_tde"]


def load_multinight_df(
        datestr: str, selection: str, lookback_days: int = 1
) -> tuple[pd.DataFrame, list[ProcStage]]:
    """
    Load a DataFrame for a given date string and lookback days

    :param datestr: str date string in 'YYYYMMDD' format
    :param selection: str selection type (e.g., 'tdescore')
    :param lookback_days: int number of days to look back
    :return: DataFrame of results
    """
    try:
        df = load_single_df(datestr, selection=selection)
    except FileNotFoundError:
        logger.warning(f"No cached results found for {datestr}")
        df = pd.DataFrame(columns=FALLBACK_COLUMNS)

    try:
        proc_log = load_processing_log(datestr, selection=selection)
    except FileNotFoundError:
        logger.warning(f"No processing log found for {datestr}")
        proc_log = []

    if lookback_days > 1:
        # Go in reverse chronological order
        old_dates = [
            (pd.to_datetime(datestr) - pd.Timedelta(days=i)).strftime('%Y%m%d')
            for i in range(1, lookback_days)
        ]

        # Only keep the first (i.e. latest) occurrence of each name
        for date in old_dates:
            try:
                old_df = load_single_df(date, selection=selection)
                mask = old_df["name"].isin(df["name"])
                old_df = old_df[~mask]

                if len(old_df) > 0:
                    df = pd.concat([df, old_df], ignore_index=True)

                new_proc_log = load_processing_log(date, selection=selection)
                proc_log = merge_processing_logs([proc_log, new_proc_log])
            except FileNotFoundError:
                logger.warning(f"File not found for date: {date}")
                continue

    return df, proc_log

def load_combined(
        datestr: str, selections: list[str], lookback_days: int = 1
) -> pd.DataFrame:
    """
    Load a DataFrame for a given date string and lookback days

    :param datestr: str date string in 'YYYYMMDD' format
    :param selections: list of str selection types (e.g., ['tdescore'])
    :param lookback_days: int number of days to look back
    :return: DataFrame of results
    """
    combined_df = pd.DataFrame(columns=FALLBACK_COLUMNS + ["selection"])
    combined_proc_log = []

    for selection in selections:
        df, _ = load_multinight_df(datestr, selection=selection, lookback_days=lookback_days)
        mask = df["name"].isin(combined_df["name"])
        df = df[~mask].copy()
        if len(df) > 0:
            df["selection"] = selection
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df
