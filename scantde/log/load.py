from scantde.paths import get_log_path
from scantde.log.model import ProcStage

import pandas as pd


def load_processing_log(datestr: str, selection: str) -> list[ProcStage]:
    """
    Load the processing log of a scantde run from a CSV file.

    :param datestr: Date string for the log file name
    :param selection: Selection string for the log file name
    :return: List of processing stages
    """

    log_path = get_log_path(datestr, selection)
    df = pd.read_json(log_path)
    return [ProcStage(**row.to_dict()) for _, row in df.iterrows()]