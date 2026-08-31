import pandas as pd
from scantde.paths import sym_dir

from scantde.database.search import load_by_name, query_by_name
from scantde.log import update_source_list, update_processing_log
from scantde.errors import NoSourcesError
from scantde.io import load_multinight_df, FALLBACK_COLUMNS

from scantde.htmlutils.make_html import make_html_single, make_daily_html_table
import numpy as np

import logging

logger = logging.getLogger(__name__)

def generate_html_by_name(name: str, selection: str) -> str:
    """
    Generate HTML for a source by name

    :param name: Name of the source
    :param selection: str selection type (e.g., 'tdescore')
    :return: HTML string
    """
    row = load_by_name(name, selection=selection)

    db_match = query_by_name(
        name, selection=selection
    )

    if row is None:
        row = db_match.copy()
        row["ra"], row["dec"] = row["latest_ra"], row["latest_dec"]
        row["thermal_window"] = None
        row["tdescore_lc_score"] = -1.
        row.replace({None: np.nan}, inplace=True)

    row["datestr"] = row["latest_datestr"]
    if pd.isnull(row["thermal_window"]):
        row["thermal_window"] = None

    output_dir = sym_dir.parent
    prefix = f"static/"

    html = make_html_single(
        row=row,
        base_output_dir=output_dir,
        selection=selection,
        prefix=prefix,
        include_cutout=True,
    )
    return html


def generate_html_by_date(
    datestr: str,
    selection: str,
    lookback_days: int = 1,
    min_score: float = 0.01,
    min_age: float = 0.0,
    hide_junk: bool = False,
    hide_classified: bool = False,
    include_cutout: bool = False,
    mode: str = "all"
) -> str:
    """
    Generate HTML for a source by name

    :param datestr: str date string in 'YYYYMMDD' format
    :param selection: str selection type (e.g., 'tdescore')
    :param min_score: float minimum score to filter candidates
    :param min_age: float minimum age to filter candidates
    :param lookback_days: int number of days to look back
    :param hide_junk: bool whether to hide old infants
    :param hide_classified: bool whether to hide classified candidates
    :param include_cutout: bool whether to include cutout images
    :param mode: str mode of operation
    :return: HTML string
    """
    df, proc_log = load_multinight_df(
        datestr, selection=selection, lookback_days=lookback_days
    )

    try:
        if hide_junk & (mode != "junk"):
            # Remove junk candidates
            mask = ~(df["is_junk"].astype(bool))

            df, proc_log = update_source_list(
                df, proc_log, mask, selection=selection,
                stage="Remove junk candidates", export_db=False
            )

        if min_age > 0.0:
            # Filter candidates by minimum age
            mask = df["age"] >= min_age

            df, proc_log = update_source_list(
                df, proc_log, mask, selection=selection,
                stage=f"Minimum age: {min_age}", export_db=False
            )

        if min_score > 0.0:
            # Filter candidates by minimum score
            mask = df["tdescore"] >= min_score

            df, proc_log = update_source_list(
                df, proc_log, mask, selection=selection,
                stage=f"Minimum score: {min_score}", export_db=False
            )

        if hide_classified:
            mask = pd.isnull(df["skyportal_class"])

            df, proc_log = update_source_list(
                df, proc_log, mask, selection=selection,
                stage="Hide classified candidates", export_db=False
            )

        mask = np.ones(len(df), dtype=bool)

        good_fit_mask = (df["thermal_score"] > 0.5) & (df["age"] < 365.0)

        if mode == "infant":
            mask *= df["age"] < 7.

        elif mode == "has-lc":
            mask *= ~df["tdescore_best"].isin(["infant", "week", "month"])

        elif mode == "junk":
            mask *= df["is_junk"].astype(bool)

        elif mode == "dwarf":
            mask *= df["is_dwarf"].astype(bool)

        elif mode == "bright":
            mask *= (df["magpsf"] < 19.0) & good_fit_mask

        elif mode == "nearby":
            mask *= (df["dist_mpc"] < 150.0) & good_fit_mask

        elif mode == "blue":
            mask *= (df["thermal_log_temp_ll"] > 4.1) & good_fit_mask

        elif mode == "red":
            mask *= (df["thermal_log_temp_ul"] < 3.9) & good_fit_mask

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=selection,
            stage=f"Mode: {mode}", export_db=False
        )

    except NoSourcesError:
        logger.warning(f"No cached results found for {datestr}")
        df = pd.DataFrame(columns=FALLBACK_COLUMNS)

    proc_log = update_processing_log(proc_log, "Final", df)

    df.sort_values(by=["tdescore"], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    output_dir = sym_dir / "tdescore" / datestr

    prefix = "static"

    html = make_daily_html_table(
        source_table=df,
        output_dir=output_dir,
        base_output_dir=sym_dir.parent,
        selection=selection,
        proc_log=proc_log,
        prefix=prefix,
        include_cutout=include_cutout,
    )
    return html