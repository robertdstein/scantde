from sqlmodel import SQLModel, create_engine
from scantde.paths import get_db_path
import logging
import sqlalchemy as sa

logger = logging.getLogger(__name__)

def get_engine(selection: str):
    """
    Get the SQLAlchemy engine for the database
    """
    sqlite_url = f"sqlite:///{get_db_path(selection)}"
    return create_engine(sqlite_url, echo=False)


def create_db_and_tables(selection: str):
    """
    Create the database and tables
    """
    engine = get_engine(selection)
    SQLModel.metadata.create_all(engine)


def check_tables_exist(selection: str):
    """
    Check if the tables exist, if not create them

    :param selection: str, the selection type (e.g., 'tdescore')
    """
    engine = get_engine(selection)
    insp = sa.inspect(engine)
    tables = insp.get_table_names()
    if len(tables) == 0:
        logger.info("No DB tables found, creating them now!")
        create_db_and_tables(selection=selection)