import pandas as pd
from tdescore.combine.parse import combine_all_sources
from tdescore.download.legacy_survey import default_catalog
from astropy.cosmology import Planck18 as cosmo
import numpy as np


def tag_dwarf(df) -> list[bool]:
    full_df = combine_all_sources(df, save=False)

    cols = [x for x in full_df.columns if "Mean" in x]

    r_mag = full_df["rMeanKronMag"]

    try:
        redshift = full_df[f"{default_catalog}_z_spec"].copy()
    except KeyError:
        redshift = pd.Series([None] * len(full_df))

    mask = pd.isnull(redshift) | (redshift < 0)
    if mask.any():
        redshift[mask] = full_df["skyportal_redshift"][mask].copy()

    mask = pd.isnull(redshift) | (redshift < 0)

    if mask.any():
        redshift[mask] = full_df[f"{default_catalog}_z_phot_median"][mask].copy()

    print(redshift)
    mask = pd.isnull(redshift) | (redshift < 0)
    print(redshift[mask])

    # Calculate the luminosity distance in parsecs
    luminosity_distance = cosmo.luminosity_distance(redshift.to_numpy(dtype=float)).to('pc').value
    # Calculate the absolute magnitude using the distance modulus formula
    dm = 5 * (np.log10(luminosity_distance) - 1)

    r_abs_mag = r_mag - dm

    dwarf_mask = (r_abs_mag > -19.0) | (pd.isnull(r_abs_mag) & (r_mag > 22.0))

    return dwarf_mask
