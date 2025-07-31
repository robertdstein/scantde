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
    df.reset_index(inplace=True, drop=True)
    windows = df["thermal_window"].replace({np.nan: None})
    keys = list(x for x in df.columns if "thermal_30.0d" in x)
    keys = [x.replace("thermal_30.0d_", "") for x in keys]
    new = {}
    for base_key in keys:
        vals = []
        for i, x in enumerate(windows):
            key = f"thermal_{x}d_{base_key}"
            try:
                vals.append(df.iloc[i][key])
            except KeyError:
                vals.append(np.nan)
        new["thermal_" + base_key] = vals

    new_df = pd.DataFrame(new)
    df = pd.concat([df, new_df], axis=1)
    return df