from pathlib import Path
import pandas as pd
from scantde.paths import sym_dir

from scantde.database.search import load_by_name
from scantde.selections.tdescore.io import load_results

from scantde.html.make_html import make_html_single, make_daily_html_table


def generate_html_by_name(name: str) -> str:
    """
    Generate HTML for a source by name

    :param name: Name of the source
    :return: HTML string
    """
    row = load_by_name(name)

    if row is None:
        return f"<p style='color:red;'>No cached results found for {name}</p>"

    row["datestr"] = row["latest_datestr"]

    output_dir = sym_dir.parent
    prefix = f"static/tdescore/"

    html = make_html_single(
        row=row,
        base_output_dir=output_dir,
        prefix=prefix,
    )
    return html


def load_df(datestr: str) -> pd.DataFrame:
    """
    Load a DataFrame for a given date string

    :param datestr: str date string in 'YYYYMMDD' format
    :return: DataFrame of results
    """
    df = load_results(datestr)
    mask = df["tdescore"] > 0.01
    df = df[mask]
    df.reset_index(inplace=True, drop=True)
    df["datestr"] = datestr
    return df


def generate_html_by_date(
        datestr: str, lookback_days: int = 1,
        hide_old_infants: bool = False,
        mode: str = "all"
) -> str:
    """
    Generate HTML for a source by name

    :param datestr: str date string in 'YYYYMMDD' format
    :param lookback_days: int number of days to look back
    :param hide_old_infants: bool whether to hide old infants
    :param mode: str mode of operation
    :return: HTML string
    """
    df = load_df(datestr)

    if lookback_days > 1:
        # Go in reverse chronological order
        old_dates = [
            (pd.to_datetime(datestr) - pd.Timedelta(days=i)).strftime('%Y%m%d')
            for i in range(1, lookback_days)
        ]

        # Only keep the first (i.e. latest) occurrence of each name

        for date in old_dates:
            try:
                old_df = load_df(date)
                mask = old_df["name"].isin(df["name"])
                old_df = old_df[~mask]

                if len(old_df) > 0:
                    df = pd.concat([df, old_df], ignore_index=True)
            except FileNotFoundError:
                print(f"File not found for date: {date}")
                continue

    df.sort_values(by=["tdescore"], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    if hide_old_infants:
        mask = df["tdescore_best"].isin(["infant", "week", "month"]) & (df["age"] > 14.)
        df = df[~mask]
        df.reset_index(drop=True, inplace=True)

    if mode == "infant":
        mask = df["age"] < 14.
        df = df[mask]
        df.reset_index(drop=True, inplace=True)

    elif mode == "non-infant":
        mask = df["age"] >= 14.
        df = df[mask]
        df.reset_index(drop=True, inplace=True)

    output_dir = sym_dir / "tdescore" / datestr

    prefix = f"static/tdescore/"

    html = make_daily_html_table(
        source_table=df,
        output_dir=output_dir,
        base_output_dir=sym_dir.parent,
        prefix=prefix
    )
    return html