from sqlmodel import Session, select, text
from scantde.database.create import engine, NuclearSource
import pandas as pd
import scantde.selections.tdescore.apply
from scantde.selections.tdescore.io import load_candidates, load_results
from scantde.selections.tdescore.make_html import make_html_single, make_daily_html_table
from scantde.paths import sym_dir



def query_by_name(name: str) -> pd.Series:
    """
    Query a model by name

    :param name: str ZTF name
    :return: SQLModel instance
    """
    with Session(engine) as session:
        stmt = select(NuclearSource).where(
            NuclearSource.name == name
        )
        res = session.exec(stmt).first()
    return pd.Series(res.model_dump()) if res else None

def load_by_name(name: str) -> pd.Series:
    """
    Load a source by name

    :param name: str ZTF name
    :return: SQLModel instance
    """
    match = query_by_name(name)
    latest = match.get("latest_datestr", None)
    df = load_results(latest)

    match = df[df["name"] == name]
    return match.iloc[0] if not match.empty else None

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
    prefix = f"static/tdescore/{row["latest_datestr"]}/"

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


def generate_html_by_date(datestr: str, lookback_days: int = 1) -> str:
    """
    Generate HTML for a source by name

    :param datestr: str date string in 'YYYYMMDD' format
    :param lookback_days: int number of days to look back
    :return: HTML string
    """
    df = load_df(datestr)

    if lookback_days > 1:
        old_dates = [
            (pd.to_datetime(datestr) - pd.Timedelta(days=i)).strftime('%Y%m%d')
            for i in range(1, lookback_days)
        ]
        all_dfs = []
        for date in old_dates:
            old_df = load_df(date)
            mask = ~old_df["name"].isin(df["name"])
            print(old_df, mask, mask.sum(), ~mask.sum())
        print(old_dates)

    output_dir = sym_dir / "tdescore" / datestr

    prefix = f"static/tdescore/{datestr}/"

    html = make_daily_html_table(
        source_table=df,
        output_dir=output_dir,
        base_output_dir=sym_dir.parent,
        prefix=prefix
    )
    return html
    # row = load_by_name(name)
    #
    # if row is None:
    #     return f"<p style='color:red;'>No cached results found for {name}</p>"
    #
    # row["datestr"] = row["latest_datestr"]
    #
    # output_dir = sym_dir.parent
    # prefix = f"static/tdescore/{row["latest_datestr"]}/"
    #
    # html = make_html_single(
    #     row=row,
    #     base_output_dir=output_dir,
    #     prefix=prefix,
    # )
    # return html

