import pandas as pd
from scantde.database.models import NuclearSource
from sqlmodel import Session
from scantde.database.create import get_engine, check_tables_exist
from erfa.core import ErfaError

from astropy.time import Time

import logging

logger = logging.getLogger(__name__)


def update_source_table(df: pd.DataFrame, selection: str, update_existing: bool = True):
    """
    Update the source table with new sources

    :param df: pd.DataFrame
    :param selection: str, the selection type (e.g., 'tdescore')
    :param update_existing: bool
    """
    check_tables_exist(selection=selection)
    engine = get_engine(selection)

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
                new_datestr = int(row["latest_datestr"])
                db_datestr =  int(source.latest_datestr)
                if new_datestr >= db_datestr:
                    for key, value in row.to_dict().items():
                        if key in source.__dict__.keys():
                            setattr(source, key, value)
                    session.commit()
                else:
                    logger.debug(
                        f"Skipping update for {row['name']}, because it is for "
                        f"an older night {new_datestr} "
                        f"than the existing entry {db_datestr}")
            else:
                logger.debug(f"Source {row['name']} already exists")


# def update_night_table(df: pd.DataFrame, datestr: str, n_initial: int = 0):
#     """
#     Update the source table with new sources
#
#     :param df: pd.DataFrame
#     :param datestr: str, date string in the format YYYYMMDD
#     :param n_initial: int, number of initial candidates
#     """
#     with Session(engine) as session:
#         res = {
#             "n_candidates": len(df), # Number in database
#             "n_tdes": int((df["is_tde"] == True).sum()),
#             "n_initial": n_initial,
#         }
#         night = session.get(Night, datestr)
#
#         if night is None:
#             # This means the night does not exist
#             night = Night(
#                 datestr=datestr,
#                 **res
#             )
#             session.add(night)
#             session.commit()
#         else:
#             # Update existing night
#             for key, value in res.items():
#                 setattr(night, key, value)
#             session.commit()


def export_to_db(df: pd.DataFrame, selection: str, update_existing: bool = True):
    """
    Export the DataFrame to the database

    :param df: DataFrame containing the candidates
    :param selection: str, the selection type (e.g., 'tdescore')
    :param update_existing: Bool, whether to update existing sources or not
    :return:
    """
    if len(df) > 0:
        df["name"] = df["ztf_name"]
        df["latest_ra"] = df["ra"]
        df["latest_dec"] = df["dec"]
        df["latest_mag"] = df["magpsf"]
        df["latest_filter"] = df["fid"].map({1: "g", 2: "r", 3: "i"})

        first_dets = []

        for i, x in enumerate(df["jdstarthist"]):
            try:
                first_dets.append(Time(x, format="jd").to_datetime())
            except ErfaError:
                first_dets.append(Time(df.iloc[i]["jd"], format="jd").to_datetime())

        df["first_detected"] = first_dets
        df["age"] = df["age_estimate"]
        update_source_table(df, selection=selection, update_existing=update_existing)