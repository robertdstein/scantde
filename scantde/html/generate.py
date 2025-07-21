import pandas as pd
from scantde.paths import sym_dir

from scantde.database.search import load_by_name
from scantde.io import load_results
from scantde.log import load_processing_log, merge_processing_logs, update_source_list, update_processing_log

from scantde.html.make_html import make_html_single, make_daily_html_table
import numpy as np


def generate_html_by_name(name: str, selection: str) -> str:
    """
    Generate HTML for a source by name

    :param name: Name of the source
    :param selection: str selection type (e.g., 'tdescore')
    :return: HTML string
    """
    row = load_by_name(name, selection=selection)

    if row is None:
        return f"<p style='color:red;'>No cached results found for {name}</p>",

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
    )
    return html


def load_df(datestr: str, selection: str) -> pd.DataFrame:
    """
    Load a DataFrame for a given date string

    :param datestr: str date string in 'YYYYMMDD' format
    :param selection: str selection type (e.g., 'tdescore')
    :return: DataFrame of results
    """
    df = load_results(datestr, selection=selection).copy()
    df["datestr"] = datestr
    df["thermal_window"].replace({np.nan: None}, inplace=True)
    return df


def generate_html_by_date(
    datestr: str,
    selection: str,
    lookback_days: int = 1,
    hide_junk: bool = False,
    mode: str = "all"
) -> str:
    """
    Generate HTML for a source by name

    :param datestr: str date string in 'YYYYMMDD' format
    :param selection: str selection type (e.g., 'tdescore')
    :param lookback_days: int number of days to look back
    :param hide_junk: bool whether to hide old infants
    :param mode: str mode of operation
    :return: HTML string
    """
    df = load_df(datestr, selection=selection)

    proc_log = load_processing_log(datestr, selection=selection)

    if lookback_days > 1:
        # Go in reverse chronological order
        old_dates = [
            (pd.to_datetime(datestr) - pd.Timedelta(days=i)).strftime('%Y%m%d')
            for i in range(1, lookback_days)
        ]

        # Only keep the first (i.e. latest) occurrence of each name

        for date in old_dates:
            try:
                old_df = load_df(date, selection=selection)
                mask = old_df["name"].isin(df["name"])
                old_df = old_df[~mask]

                if len(old_df) > 0:
                    df = pd.concat([df, old_df], ignore_index=True)

                new_proc_log = load_processing_log(date, selection=selection)
                proc_log = merge_processing_logs([proc_log, new_proc_log])
            except FileNotFoundError:
                print(f"File not found for date: {date}")
                continue

    mask = df["tdescore"] > 0.01
    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage="TDE Score > 0.01", export_db=False
    )

    if hide_junk & (mode != "junk"):
        # Remove junk candidates
        mask = ~(df["is_junk"])

        df, proc_log = update_source_list(
            df, proc_log, mask, selection=selection,
            stage="Remove junk candidates", export_db=False
        )

    mask = np.ones(len(df), dtype=bool)

    if mode == "infant":
        mask *= df["age"] < 7.

    elif mode == "has-lc":
        mask *= ~df["tdescore_best"].isin(["infant", "week", "month"])

    elif mode == "junk":
        mask *= df["is_junk"]

    elif mode == "bright":
        mask *= df["magpsf"] < 19.0

    df, proc_log = update_source_list(
        df, proc_log, mask, selection=selection,
        stage=f"Mode: {mode}", export_db=False
    )

    proc_log = update_processing_log(proc_log, "Final", df)

    df.sort_values(by=["tdescore"], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    output_dir = sym_dir / "tdescore" / datestr

    prefix = f"static"

    html = make_daily_html_table(
        source_table=df,
        output_dir=output_dir,
        base_output_dir=sym_dir.parent,
        selection=selection,
        proc_log=proc_log,
        prefix=prefix
    )
    return html