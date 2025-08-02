import pandas as pd
import numpy as np

def relabel_fields(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Relabel fields in the DataFrame to add "thermal_" prefix to keys
    based on the "thermal_window" column. E.g. "thermal_rb" will be copied from
    "thermal_30.0d_rb" if the thermal window is 30.0 days.

    :param df: DataFrame with source data
    :return: DataFrame with relabeled fields
    """

    all_new = []

    for i, row in df.iterrows():

        new = {"ztf_name": row["ztf_name"]}
        window = row["thermal_window"]

        thermal_key = f"thermal_{window}d_" if pd.notnull(window) else f"thermal_Noned_"

        keys = list(x for x in df.columns if thermal_key in x)

        for key in keys:
            new[key.replace(thermal_key, "thermal_")] = row[key]

        all_new.append(new)

    new_df = pd.DataFrame(all_new)
    new_df.set_index("ztf_name", inplace=True)
    return new_df