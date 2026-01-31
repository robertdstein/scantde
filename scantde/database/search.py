from sqlmodel import Session, select
from scantde.database import NuclearSource
from scantde.database.create import get_engine
import pandas as pd
from scantde.io import load_results


def query_by_name(name: str, selection: str) -> pd.Series:
    """
    Query a model by name

    :param name: str ZTF name
    :param selection: str selection type (e.g., 'tdescore')
    :return: SQLModel instance
    """
    engine = get_engine(selection=selection)
    with Session(engine) as session:
        stmt = select(NuclearSource).where(
            NuclearSource.name == name
        )
        res = session.exec(stmt).first()
    return pd.Series(res.model_dump()) if res else None


def load_by_name(name: str, selection: str) -> pd.Series:
    """
    Load a source by name

    :param name: str ZTF name
    :param selection: str selection type (e.g., 'tdescore')
    :return: SQLModel instance
    """
    match = query_by_name(name, selection)
    latest = match.get("latest_datestr", None)
    df = load_results(latest, selection=selection)

    match = df[df["name"] == name]
    return match.iloc[0] if not match.empty else None

