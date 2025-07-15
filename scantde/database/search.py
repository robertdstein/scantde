from sqlmodel import Session, select, text
from scantde.database.create import engine, NuclearSource
import pandas as pd
import scantde.selections.tdescore.apply
from scantde.selections.tdescore.io import load_candidates, load_results
from scantde.selections.tdescore.make_html import make_html_single, TDESCORE_HTML_DIR



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

    row = df[df["name"] == name].iloc[0]
    return row

def generate_html_by_name(name: str) -> str:
    """
    Generate HTML for a source by name

    :param name: Name of the source
    :return: HTML string
    """
    row = load_by_name(name)
    row["datestr"] = row["latest_datestr"]

    output_dir = TDESCORE_HTML_DIR / str(row["latest_datestr"])
    prefix = f"static/tdescore/{row["latest_datestr"]}/"

    html = make_html_single(
        row=row,
        base_output_dir=output_dir,
        prefix=prefix,
    )
    return html

