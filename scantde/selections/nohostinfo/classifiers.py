"""
Centralized location for applying classifiers to a given dataset
"""

import logging
from pathlib import Path
from typing import Optional

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from tdescore.classifier.collate import convert_to_train_dataset
from tdescore.classifier.features import (
    fast_host_columns,
    host_columns,
    parse_columns,
    infant_columns,
    week_columns,
    month_columns,
    post_peak,
    get_thermal_columns,
)
from xgboost import XGBClassifier

from scantde.paths import ml_dir

logger = logging.getLogger(__name__)


def apply_classifier(
    source_table: pd.DataFrame,
    classifier: str,
    selection: str,
    shap_base_dir: Optional[Path] = None,
    explain: bool = True,
):

    window = classifier.split("_")[-1]
    try:
        window = float(window)
        classifier_name = f"thermal_nohostinfo_{window:.0f}"
    except ValueError:
        window = None
        classifier_name = "thermal_nohostinfo_all"
    columns = get_thermal_columns(window, include_host=False)

    tdescore_path = ml_dir.joinpath(f"{classifier_name}.json")
    clf = XGBClassifier()
    clf.load_model(str(tdescore_path))

    train_data = ml_dir.joinpath(f"tdescore_train_data.pkl")
    train_data = joblib.load(train_data)

    relevant_columns, column_descriptions = parse_columns(columns)

    try:
        data_to_use = convert_to_train_dataset(source_table, columns=relevant_columns)
    except KeyError as e:
        logger.error(f"Failed to parse columns: {e}")
        return np.array([]), np.ones(len(source_table), dtype=bool)

    for i, col in enumerate(relevant_columns):
        nan_count = pd.isnull(data_to_use.T[i]).sum()
        if nan_count > 0:
            logger.debug(
                f"{nan_count}/{len(data_to_use)} sources are missing entry '{col}'"
            )
    nan_mask = np.array([np.sum(pd.isnull(x)) > 0 for x in data_to_use], dtype=bool)

    data_to_use = data_to_use[~nan_mask].astype(float)

    logger.info(f"Applying classifier: {classifier_name}")

    scores = clf.predict_proba(data_to_use).T[1] if len(data_to_use) > 0 else np.array([])

    if explain & (len(data_to_use) > 0):
        if shap_base_dir is None:
            raise ValueError("shap_base_dir must be provided if explain=True")

        shap_output_dir = shap_base_dir.joinpath(classifier)

        shap_output_dir.mkdir(parents=True, exist_ok=True)

        # Load the training data and use it to explain the classifier
        train_array = convert_to_train_dataset(train_data, columns=relevant_columns)
        train_nan_mask = np.array([np.sum(pd.isnull(x)) > 0 for x in train_array])
        train_array = train_array[~train_nan_mask].astype(float)
        explainer = shap.Explainer(clf, train_array, feature_names=relevant_columns)

        # Apply explainer to the new data
        shap_values = explainer(data_to_use)

        for i, shap_value in enumerate(shap_values):

            source_name = source_table[~nan_mask]["ztf_name"].to_list()[i]

            save_path = shap_output_dir.joinpath(f"{source_name}.png")

            fig = plt.figure()

            shap.plots.waterfall(shap_value, max_display=5, show=False)

            plt.title(f"{source_name} (tdescore_{classifier_name}={scores[i]:.4f})")
            plt.savefig(save_path, bbox_inches="tight")
            plt.close(fig)

    return scores, nan_mask
