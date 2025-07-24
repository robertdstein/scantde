import pandas as pd
from tdescore.lightcurve.extinction import get_extinction_correction, wavelengths, extra_wavelengths

all_wavelengths = wavelengths.copy()
all_wavelengths.update(extra_wavelengths)

ext_keys = [f"ext_{name}" for name in all_wavelengths.keys()]

def get_extinction_dict(
    row: pd.Series
) -> dict[str, float]:
    """
    Get extinction corrections for a row in a DataFrame.

    :param row: Row containing 'ra' and 'dec' columns.
    :return: New dictionary with extinction corrections for each wavelength.
    """
    new = {}
    ra, dec = row["ra"], row["dec"]
    for f_name, wl in all_wavelengths.items():
        extinction = get_extinction_correction(ra, dec, [wl])
        new[f"ext_{f_name}"] = extinction[0]
    return new

def append_extinction_to_df(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Append extinction corrections to a DataFrame.

    :param df: DataFrame with 'ra' and 'dec' columns.
    :return: DataFrame with additional columns for extinction corrections.
    """
    if "ra" not in df.columns or "dec" not in df.columns:
        raise ValueError("DataFrame must contain 'ra' and 'dec' columns.")

    ext_dicts = df.apply(get_extinction_dict, axis=1)
    ext_df = pd.DataFrame(list(ext_dicts))

    return pd.concat([df, ext_df], axis=1)