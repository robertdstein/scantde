import pandas as pd

from pathlib import Path
from scantde.log.model import ProcStage
from scantde.paths import get_log_path

import logging

logger = logging.getLogger(__name__)

def export_processing_log(
    proc_log: list[ProcStage],
    datestr: str,
    selection: str,
) -> None:
    """
    Export the processing log of scantde run to a CSV file.

    :param proc_log: List of processing stages
    :param datestr: Date string for the log file name
    :param selection: Selection string for the log file name
    """

    df = pd.DataFrame([stage.model_dump() for stage in proc_log])
    log_path = get_log_path(datestr, selection)
    logger.info(f"Exporting processing log to {log_path}")
    df.to_json(log_path, index=False)