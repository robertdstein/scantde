import logging

from pathlib import Path

import pandas as pd

from tdescore.combine.parse import combine_all_sources
from tdescore.lightcurve.analyse import batch_analyse, batch_analyse_thermal
from tdescore.sncosmo.run_sncosmo import batch_sncosmo
from tdescore.lightcurve.thermal import THERMAL_WINDOWS
import numpy as np
from scantde.selections.utils.classifiers import apply_classifier

logger = logging.getLogger(__name__)

def apply_thermal(
    df: pd.DataFrame,
    selection: str,
    base_output_dir: Path,
) -> pd.DataFrame:
    """
    Apply the thermal classifier to a given source table.
    Selects the best thermal window for each source based on its age, and only applies the LC fitting for that window.

    :param df: DataFrame containing source data
    :param selection: Selection name to use for the classifier (e.g. 'tdescore')
    :param base_output_dir: Base output directory for results
    :return: DataFrame with classification results
    """
    logger.info("Applying thermal lightcurve classifier")

    gp_output_dir = base_output_dir / f"gp"
    gp_output_dir.mkdir(parents=True, exist_ok=True)

    shap_base_dir = base_output_dir / f"{selection}/shap"

    df.reset_index(drop=True, inplace=True)
    full_df = combine_all_sources(df, save=False)

    best_windows = []

    for i, row in full_df.iterrows():
        windows = [x for x in THERMAL_WINDOWS if x is not None]
        windows = [x for x in windows if row["age"] > x]
        idx = len(windows)
        window = (THERMAL_WINDOWS + THERMAL_WINDOWS[-1:])[idx]
        best_windows.append(window)

    df["thermal_window"] = best_windows

    windows = []

    for window in THERMAL_WINDOWS:

        logger.info(f"Analysing thermal data for window {window}")

        mask = df["thermal_window"] == window \
            if window is not None else df["thermal_window"].isnull()

        if mask.sum() == 0:
            logger.info(f"No sources have thermal data for window {window}")
            continue

        logger.info(f"{sum(mask)} sources have thermal data for window {window}")

        batch_analyse_thermal(
            df["ztf_name"][mask & ~df["tdescore_lc"]],
            overwrite=True,
            base_output_dir=gp_output_dir,
            thermal_windows=[window],
        )
        # Run sncosmo on the data in the thermal window
        batch_sncosmo(
            full_df["ztf_name"][mask & ~df["tdescore_lc"]], overwrite=True,
            windows=[window],
        )

        windows.append(window)

    full_df = combine_all_sources(df, save=False)

    for window in windows:

        scores, nan_mask = apply_classifier(
            full_df, f"thermal_{window}", selection=selection, explain=True,
            shap_base_dir=shap_base_dir
        )

        mask = df["thermal_window"] == window \
            if window is not None else df["thermal_window"].isnull()

        base_name = f"thermal_{window:.0f}" if window is not None else "thermal_all"
        label = f"tdescore_{base_name}"

        if len(scores) == 0:
            logger.warning(f"No scores found for window {window}, skipping")
            continue

        df[label] = np.nan
        df.loc[~nan_mask, [label]] = scores
        df.loc[(~nan_mask) & mask, ["tdescore"]] = scores[mask[~nan_mask]]
        df.loc[(~nan_mask) & mask, ["tdescore_best"]] = base_name
        df.loc[(~nan_mask) & mask, ["tdescore_high_noise"]] = full_df[f"thermal_{window}d_high_noise"][mask]
        df.loc[(~nan_mask) & mask, ["tdescore_lc_score"]] = full_df[f"thermal_{window}d_score"][mask]

    df["age_estimate"] = full_df["age"]

    return df