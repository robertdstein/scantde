import pandas as pd

from pathlib import Path
from scantde.utils.plot import create_lightcurve_plots
from tdescore.sncosmo.run_sncosmo import batch_sncosmo
from tdescore.lightcurve.analyse import batch_analyse

import logging

logger = logging.getLogger(__name__)



def apply_lightcurve(
    df: pd.DataFrame,
    base_output_dir: Path,
):
    logger.info("Making lightcurve plots")
    create_lightcurve_plots(df, base_output_dir)  # FIXME: full_df ?

    logger.info("Running GP / SNcosmo analysis on full lightcurve data")

    gp_output_dir = base_output_dir / "gp"
    gp_output_dir.mkdir(parents=True, exist_ok=True)
    batch_analyse(
        df["ztf_name"][~df["tdescore_lc"]],
        overwrite=True,
        include_text=False,
        base_output_dir=gp_output_dir,
        thermal_windows=[],
    )
    # Only run on the full lightcurve data
    batch_sncosmo(
        df["ztf_name"][~df["tdescore_lc"]],
        overwrite=True,
        windows=[None],
    )

    # df.loc[~nan_mask, ["tdescore"]] = scores
    # df.loc[~nan_mask, ["tdescore_best"]] = "full"
    # df.loc[high_noise_mask, ["tdescore"]] = -1.0