"""
Selection functions for samples derived from tdescore
"""
import pandas as pd
from scantde.utils.skyportal import export_to_skyportal


def selection_thermal(df: pd.DataFrame, window: float) -> pd.DataFrame:
    """
    Select candidates that have been observed for at least 30 days
    """

    thermal_columns = [
        col for col in df.columns if ("tdescore_thermal_" in col)
    ]
    thermal_columns = [
        col for col in thermal_columns if float(col.split("_")[-1]) > window
    ]

    n_scores = df[thermal_columns].notnull().sum(axis=1)

    key = f"tdescore_thermal_{window:.1f}"

    if key not in df:
        return pd.DataFrame()

    mask = (
        (df[key] >= 0.5)
        & (n_scores > 0)
    )
    return df[mask]


def export_thermal_selection(df: pd.DataFrame, window: float, group_id: int):
    """
    Function to manage the 30 day selection
    """
    df_cut = selection_thermal(df, window=window)
    print(f"Exporting {len(df_cut)} sources to SkyPortal with group_id {group_id} and window {window} days")
    export_to_skyportal(df_cut, group_id=group_id)


def selection_cut(df: pd.DataFrame, key: str, min_age: float | None = None, max_age: float | None = None) -> pd.DataFrame:
    """
    Select candidates that meet a minimum TDEScore threshold
    """

    key = f"tdescore_{key}"

    if key not in df.columns:
        return pd.DataFrame()

    mask = (df[key] >= 0.5)

    if min_age is not None:
        mask = mask & (df["age"].astype(float) > min_age)

    if max_age is not None:
        mask = mask & (df["age"].astype(float) < max_age)

    return df[mask]


def export_cut_selection(df: pd.DataFrame, key: str, group_id: int, min_age: float | None = None, max_age: float | None = None):
    """
    Function to manage the TDEScore threshold selection
    """
    df_cut = selection_cut(df, key=key, min_age=min_age, max_age=max_age)
    if len(df_cut) > 0:
        print(f"Exporting {len(df_cut)} sources to "
              f"SkyPortal with group_id {group_id} and key {key}")

        print(df_cut[["ztf_name", "age"]])
        export_to_skyportal(df_cut, group_id=group_id)


thermal_export_map = {
    "14": "1857",
    "30": "1734",
    "60": "1735",
    "90": "1736",
    "180": "1737",
    "365": "1858",
}

cut_export_map = {
    "thermal_all": ["1859", 365.0, None],
    "full": ["1738", None, None],
}


def export_selections(df: pd.DataFrame):
    """
    Export the selections to a CSV file
    """
    for window, group_id in thermal_export_map.items():
        export_thermal_selection(df, window=float(window), group_id=int(group_id))

    for key, (group_id, min_age, max_age) in cut_export_map.items():
        export_cut_selection(
            df, key=key, group_id=int(group_id), min_age=min_age, max_age=max_age
        )
