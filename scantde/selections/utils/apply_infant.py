import pandas as pd
import numpy as np

from pathlib import Path

from tdescore.combine.parse import combine_all_sources
from scantde.selections.utils.classifiers import apply_classifier
from scantde.log import update_source_list
from scantde.log.model import ProcStage

import logging

logger = logging.getLogger(__name__)

def apply_infant(
    df: pd.DataFrame,
    selection: str,
    proc_log: list[ProcStage],
    base_output_dir: Path
) -> tuple[pd.DataFrame, list[ProcStage]]:
    full_df = combine_all_sources(df, save=False)

    shap_base_dir = base_output_dir / f"{selection}/shap"

    scores, nan_mask = apply_classifier(
        full_df, "infant", selection=selection, explain=True,
        shap_base_dir=shap_base_dir
    )

    df, proc_log = update_source_list(
        df, proc_log, ~nan_mask, selection=selection,
        stage="TDEScore nans with infant data"
    )

    df["tdescore_infant"] = scores
    df["tdescore"] = scores
    df["tdescore_best"] = "infant"

    df.sort_values(by="tdescore_infant", inplace=True, ascending=False)
    df.reset_index(drop=True, inplace=True)

    logger.info(f"Assigning scores to {len(scores)} sources with later data")

    # From here we assign scores if data is available but don't cut on them
    full_df = combine_all_sources(df.copy(), save=False)
    scores, nan_mask = apply_classifier(
        full_df, "week", selection=selection, explain=True,
        shap_base_dir=shap_base_dir
    )
    df["tdescore_week"] = np.nan
    df.loc[~nan_mask, ["tdescore_week"]] = scores
    df.loc[~nan_mask, ["tdescore"]] = scores
    df.loc[~nan_mask, ["tdescore_best"]] = "week"

    return df, proc_log