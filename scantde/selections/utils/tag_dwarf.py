import pandas as pd
from tdescore.combine.parse import combine_all_sources
from tdescore.download.legacy_survey import default_catalog
from astropy.cosmology import Planck18 as cosmo
import numpy as np


def tag_dwarf(df) -> pd.DataFrame:
    full_df = combine_all_sources(df, save=False)

    r_mag = full_df["rMeanKronMag"].astype(float)

    try:
        redshift = full_df[f"{default_catalog}_z_spec"].copy()
    except KeyError:
        redshift = pd.Series([None] * len(full_df))

    mask = pd.isnull(redshift) | (redshift < 0)
    if mask.any():
        redshift[mask] = full_df["skyportal_redshift"][mask].copy()

    mask = pd.isnull(redshift) | (redshift < 0)

    if mask.any():
        try:
            redshift[mask] = full_df[f"{default_catalog}_z_phot_median"][mask].copy()
        except KeyError:
            pass

    mask = pd.isnull(redshift) | (redshift < 0)

    # Calculate the luminosity distance in parsecs
    luminosity_distance = cosmo.luminosity_distance(redshift[~mask].to_numpy(dtype=float)).to('pc').value

    dist_mpc = np.ones_like(redshift, dtype=float) * np.nan
    dist_mpc[~mask] = luminosity_distance / 1e6  # Convert parsecs to megaparsecs

    # Calculate the absolute magnitude using the distance modulus formula
    dm = 5 * (np.log10(luminosity_distance) - 1)

    r_abs_mag = pd.Series([np.nan] * len(r_mag), index=r_mag.index)
    r_abs_mag[~mask] = r_mag[~mask] - dm

    df["host_r"] = r_mag
    df["host_Mr"] = r_abs_mag
    df["dist_mpc"] = dist_mpc
    df["best_redshift"] = redshift
    df["is_dwarf"] = (r_abs_mag > -19.0) | (pd.isnull(r_abs_mag) & (r_mag > 22.0))

    return df
