from sqlmodel import Session, select
from scantde.database.create import engine, NuclearSource
import pandas as pd
from scantde.selections.tdescore.io import load_results



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

