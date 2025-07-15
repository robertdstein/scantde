from scantde.database.models._source import NuclearSource
from sqlmodel import SQLModel, create_engine, Session
from scantde.paths import db_path
import pandas as pd
import logging
import sqlalchemy as sa

logger = logging.getLogger(__name__)

sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    """
    Create the database and tables
    """
    SQLModel.metadata.create_all(engine)


def check_tables_exist():
    """
    Check if the tables exist, if not create them
    """
    insp = sa.inspect(engine)
    tables = insp.get_table_names()
    if len(tables) == 0:
        print("No DB tables found, creating them now!")
        create_db_and_tables()


check_tables_exist()


def update_source_table(df: pd.DataFrame, update_existing: bool = False):
    """
    Update the source table with new sources

    :param df: pd.DataFrame
    :param update_existing: bool
    """
    with Session(engine) as session:
        for idx, row in df.iterrows():

            source = session.get(NuclearSource, row["name"])

            if source is None:
                # This means the source does not exist
                source = NuclearSource(
                    **row.to_dict()
                )
                session.add(source)
                session.commit()
            elif update_existing:
                source = session.get(NuclearSource, row["name"])
                for key, value in row.to_dict().items():
                    if key in source.__dict__.keys():
                        setattr(source, key, value)
                session.commit()
            else:
                logger.debug(f"Source {row['name']} already exists")
