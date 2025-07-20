"""
Module for plotting lightcurves
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tdescore.alerts import load_source_raw
from tdescore.lightcurve.plot import FIG_HEIGHT, FIG_WIDTH
from tdescore.lightcurve.extinction import apply_extinction_correction
from tdescore.download.legacy_survey import default_catalog
from astropy.cosmology import Planck18 as cosmo
import numpy as np



def create_lightcurve_plots(source_table: pd.DataFrame, base_output_dir: Path):
    """
    Create lightcurve plots for a table of sources

    :param source_table: Table of sources
    :param base_output_dir: Output directory
    """

    fig_dir = base_output_dir / "lightcurves"
    fig_dir.mkdir(parents=True, exist_ok=True)

    for i, row in source_table.iterrows():
        source_name = row["ztf_name"]

        fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
        ax = plt.subplot(111)
        output_path = fig_dir / f"{source_name}.png"

        raw_df = load_source_raw(source_name)

        raw_df["days"] = raw_df["jd"] - raw_df["jd"].max()

        raw_df = raw_df[raw_df["isdiffpos"].astype(str).isin(["t", "1", "true", "True"])]

        colors = {
            1: "green",
            2: "red",
            3: "orange",
        }
        raw_df = apply_extinction_correction(raw_df)

        for fid in set(raw_df["fid"]):
            mask = raw_df["fid"] == fid
            lc = raw_df[mask]
            ax.errorbar(
                lc["days"],
                lc["magpsf"],
                yerr=lc["sigmapsf"],
                color=colors[int(fid)],
                fmt="o",
                markersize=2,
            )

        try:
            redshift = row[f"{default_catalog}_z_spec"] if row[f"{default_catalog}_z_spec"] > 0 \
                else row[f"{default_catalog}_z_phot_median"]
            label = "spec" if row[f"{default_catalog}_z_spec"] > 0 else "phot"
        except KeyError:
            redshift = -99.
            label = "none"

        if label == "phot":
            if pd.notnull(row["skyportal_redshift"]):
                if row["skyportal_redshift"] > 0:
                    # Use skyportal redshift if available
                    redshift = row["skyportal_redshift"]
                    label = "fritz_"

        if redshift > 0:
            # Calculate the luminosity distance in parsecs
            luminosity_distance = cosmo.luminosity_distance(redshift).to('pc').value
            # Calculate the absolute magnitude using the distance modulus formula
            dm = 5 * (np.log10(luminosity_distance) - 1)

            # Plot the absolute magnitude
            ax2 = ax.twinx()
            ax2.invert_yaxis()
            for fid in set(raw_df["fid"]):
                mask = raw_df["fid"] == fid
                lc = raw_df[mask]
                ax2.errorbar(
                    lc["days"],
                    lc["magpsf"] - dm,
                    yerr=lc["sigmapsf"],
                    color=colors[int(fid)],
                    fmt="o",
                    markersize=2,
                )
            ax2.set_ylabel(f"Ab Mag [AB] ({label}z={redshift:.2f})")

        ax.set_xlabel("Days Ago")
        ax.set_ylabel("Mag [AB]")
        ax.invert_yaxis()

        sns.despine(right=False)

        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)
