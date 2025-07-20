from scantde.log.model import ProcStage
from scantde.errors import NoSourcesError


import logging

import pandas as pd
from scantde.database import export_to_db

logger = logging.getLogger(__name__)


def update_processing_log(
    proc_log: list[ProcStage],
    stage: str,
    df: pd.DataFrame,
) -> list[ProcStage]:
    """
    Update the processing log with the latest data

    :param proc_log: List of processing stages
    :param stage: The current processing stage
    :param df: DataFrame containing the sources
    :return: Updated processing log
    """
    proc_log.append(ProcStage(**{
        "stage": stage,
        "n_sources": len(df),
        "tdes": [row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]],
    }))
    return proc_log


def update_source_list(
    df: pd.DataFrame,
    proc_log: list[ProcStage],
    mask: pd.Series,
    selection: str,
    stage: str,
    export_db: bool = True,
) -> tuple[pd.DataFrame, list[ProcStage]]:
    """
    Update the source table with the latest data
    """
    logger.info(
        f"Applying '{stage}' cut, "
        f"leaving {sum(mask)} sources including {sum(df['is_tde'])} TDEs"
    )

    proc_log = update_processing_log(proc_log, stage, df)

    if export_db:
        rejected_sources = df[~mask].copy()
        rejected_sources["fail_step"] = stage
        export_to_db(rejected_sources, selection=selection, update_existing=False)

    if len(df) == 0:
        raise NoSourcesError("No sources left after cut")

    return df[mask], proc_log