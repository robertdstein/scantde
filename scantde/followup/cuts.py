"""
Basic filter for follow-up
"""
import pandas as pd

def apply_base_spec_cuts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cuts to the follow-up DataFrame

    :param df: DataFrame of sources
    :return: List of unclassified likely-real sources
    """
    # Define the cuts to be applied
    mask = (
        pd.isnull(df["skyportal_class"])
        & (df["tdescore"] > 0.1)
        & (df["thermal_score"] > 0.5)
        & (df["age"] < 365.0)
        & ~(df["is_junk"].astype(bool))
    )

    return df[mask]