import pandas as pd
import numpy as np

from tdescore.combine.parse import combine_all_sources
from scantde.selections.utils.classifiers import apply_classifier
from scantde.log import update_processing_log, update_source_list
from scantde.log.model import ProcStage
from pathlib import Path

def apply_full(
    df: pd.DataFrame,
    base_output_dir: Path,
    selection: str,
):
    """
    Function to apply the full TDEScore selection to a table of sources.

    :param df: Table of sources
    :param base_output_dir: Directory to save output
    :param selection: Selection name, default is "tdescore"
    """
    shap_base_dir = base_output_dir / f"{selection}/shap"

    full_df = combine_all_sources(df, save=False)
    scores, nan_mask = apply_classifier(
        full_df, "full", selection=selection, explain=True,
        shap_base_dir=shap_base_dir
    )
    df["tdescore_full"] = np.nan
    df.loc[~nan_mask, ["tdescore_full"]] = scores

    return df

    # high_noise_mask = pd.notnull(full_df["high_noise"]) & full_df["high_noise"]
    # df, proc_log = update_source_list(
    #     df, proc_log, ~high_noise_mask, selection=selection,
    #     stage="TDEScore High Noise Sources"
    # )
    # df.loc[high_noise_mask, ["tdescore_full"]] = -1.0

