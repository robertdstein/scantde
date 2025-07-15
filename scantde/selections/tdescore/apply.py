"""
Module for integrating the TDEScore into the TDE pipeline.
(https://arxiv.org/abs/2312.00139)
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.time import Time
from tqdm import tqdm

# from scantde.auth import auth_kowalski
# from scantde.paths import sfd_dir, tdescoredir

# # Copy the settings from this code to TDEscore
# os.environ["TDESCORE_DATA"] = str(tdescoredir)
# if len(auth_kowalski) == 1:
#     os.environ["KOWALSKI_TOKEN"] = str(auth_kowalski[0])

from tdescore.combine.parse import combine_all_sources
from tdescore.download.all import (
    download_all,
    download_fritz_data,
    download_gaia_data,
    download_panstarrs_data,
    download_ps1strm_data,
    download_sdss_data,
    download_tns_data,
    download_wise_data,
    download_legacy_survey_data,
)
from tdescore.download.tns import download_tns_data
from tdescore.lightcurve.analyse import batch_analyse, batch_analyse_thermal
from tdescore.lightcurve.thermal import THERMAL_WINDOWS
from tdescore.paths import data_dir, sfd_path
from tdescore.raw import load_raw_sources
from tdescore.raw.extract import combine_raw_source_data
from tdescore.raw.ztf import download_alert_data, ZTF_BACKEND
from tdescore.sncosmo.run_sncosmo import batch_sncosmo
from tdescore.lightcurve.thermal import (
    analyse_source_thermal
)

from scantde.selections.tdescore.classifiers import apply_classifier
from scantde.selections.tdescore.make_html import make_daily_html_table, INFANT_HTML_NAME
from scantde.selections.tdescore.plot import create_lightcurve_plots
from scantde.utils.skyportal import export_to_skyportal, download_from_skyportal
from scantde.selections.tdescore.io import save_candidates, save_results
from scantde.selections.tdescore.archive import update_archive
from astropy.coordinates import SkyCoord

from scantde.database import update_source_table


logger = logging.getLogger(__name__)

# # Symlink the SFD dust map
# if not sfd_path.exists():
#     sfd_path.parent.mkdir(parents=True, exist_ok=True)
#     sfd_path.symlink_to(sfd_dir)
#     logger.info(f"Symlinked SFD dust map from {sfd_dir} to {sfd_path}")


class NoSourcesError(Exception):
    """
    No sources error
    """


def download_crossmatch_fast(source_table: pd.DataFrame):
    """
    Function to download crossmatch data from external catalogues
    """
    logger.info("Downloading PS1STRM data")
    download_ps1strm_data(source_table)
    logger.info("Downloading Gaia data")
    download_gaia_data(source_table)
    logger.info("Downloading PanSTARRS data")
    download_panstarrs_data(source_table)


def export_to_db(df: pd.DataFrame, update_existing: bool = True):
    if len(df) > 0:
        df["name"] = df["ztf_name"]
        df["latest_ra"] = df["ra"]
        df["latest_dec"] = df["dec"]
        df["first_detected"] = [
            Time(x, format="jd").to_datetime() for x in df["jdstarthist"]
        ]
        update_source_table(df, update_existing=update_existing)


def update_source_list(
    df: pd.DataFrame,
    proc_log: list[dict],
    mask: pd.Series,
    stage: str,
    export_db: bool = True,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Update the source table with the latest data
    """
    logger.info(
        f"Applying '{stage}' cut, "
        f"leaving {sum(mask)} sources including {sum(df['is_tde'])} TDEs"
    )

    proc_log.append({
        "stage": stage,
        "n_sources": len(df),
        "tdes": [row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]],
    })

    if export_db:
        rejected_sources = df[~mask].copy()
        rejected_sources["fail_step"] = stage
        export_to_db(rejected_sources, update_existing=False)

    if len(df) == 0:
        raise NoSourcesError("No sources left after cut")

    return df[mask], proc_log


def apply_tdescore(
    df: pd.DataFrame,
    base_output_dir: Path,
):
    """
    Function to apply the TDEScore to a table of sources

    :param df: Table of sources
    :param base_output_dir: Directory to save output
    """

    datestr = base_output_dir.name
    t_max_jd = Time(
        f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}T15:00:00.0", format='isot'
    ).jd

    proc_log = []

    if len(df) == 0:
        logger.warning("Source table is empty, generating empty HTML table")
        make_daily_html_table(pd.DataFrame(columns=["is_tde", "ztf_name"]), base_output_dir)
        return

    try:

        shap_base_dir = base_output_dir / "tdescore/shap"

        logger.info(f"Starting with {len(df)} sources, including {sum(df['is_tde'])} TDE alerts")
        logger.info(f"These TDEs are: {set(df[df['is_tde']]['ztf_name'].to_list())}")

        proc_log.append({
            "stage": "Initial",
            "n_sources": len(df),
            "tdes": list(set([row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]])),
        })

        max_sgscore = 0.5

        mask = (df["sgscore1"] < max_sgscore) & (df["sgscore1"] > -999.0)
        df = df[mask].copy()

        logger.info(f"Applying sgscore cut, leaving {len(df)} sources including {sum(df['is_tde'])} TDEs")

        proc_log.append({
            "stage": "Algorithmic cuts - sgscore",
            "n_sources": len(df),
            "tdes": list(set([row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]]))
        })

        if len(df) == 0:
            raise NoSourcesError("No sources left after cut")

        # Deduplicate

        logger.info("Deduplicating sources")

        new = []

        for name in tqdm(set(df["ztf_name"])):
            mask = df["ztf_name"] == name
            df_cut = df[mask].sort_values(by="jd")
            new.append(df_cut.iloc[0])

        df = pd.DataFrame(new)
        df = df.sort_values(by=["is_tde", "ztf_name"], ascending=[False, False])
        df.reset_index(drop=True, inplace=True)

        logger.info(f"Have {len(df)} unique sources, including {sum(df['is_tde'])} TDEs")

        proc_log.append({
            "stage": "De-duplicated",
            "n_sources": len(df),
            "tdes": [row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]],
        })

        max_dist = 0.9

        mask = df["distpsnr1"] < max_dist

        df, proc_log = update_source_list(
            df, proc_log, mask, "Algorithmic cuts - nuclear distance", export_db=False
        )

        logger.info(f"Applying nuclear distance cut, leaving {len(df)} sources")

        c = SkyCoord(ra=df["ra"].values, dec=df["dec"].values, unit="deg")
        df["gal_b"] = c.galactic.b.deg

        min_gal_b = 10

        mask = (df["gal_b"] < -min_gal_b) | (df["gal_b"] > min_gal_b)

        df, proc_log = update_source_list(
            df, proc_log, mask, "Algorithmic cuts - Galactic latitude", export_db=False
        )

        logger.info(
            f"Applying Galactic latitude cut (|b| > {min_gal_b}), "
            f"leaving {len(df)} sources"
        )

        mask = np.ones(len(df), dtype=bool)

        for column in ["sgmag1", "srmag1", "simag1", "szmag1"]:
            mask &= (df[column] > 12.) | (df[column] == -999.)

        df, proc_log = update_source_list(
            df, proc_log, mask, "Algorithmic cuts - bright host (stellar)", export_db=False
        )

        logger.info(
            f"Applying bright host (stellar) cut, leaving {len(df)} sources"
        )

        mask = (df["neargaiabright"] > 5.) | (df["neargaiabright"] < -0.0)

        df, proc_log = update_source_list(
            df, proc_log, mask, "Algorithmic cuts - neargaiabright", export_db=False
        )

        logger.info(
            f"Applying neargaiabright cut, leaving {len(df)} sources"
        )

        # Apply the first classifier which uses fast crossmatch data (no WISE)

        logger.info("Downloading fast crossmatch data")
        download_crossmatch_fast(df.copy())
        logger.info("Combining fast crossmatch sources")
        full_df = combine_all_sources(df.copy(), save=False)
        mask = (full_df["gaia_aplx"] < 3.0) & ~full_df["has_milliquas"]

        df, proc_log = update_source_list(
            df, proc_log, mask, "Algorithmic crossmatch cuts - fast"
        )

        # Fast host crossmatch data
        # full_df = full_df[mask]
        # scores, nan_mask = apply_classifier(full_df, "hostfast", explain=False)
        #
        # df, proc_log = update_source_list(
        #     df, proc_log, ~nan_mask, "TDEScore nans with fast crossmatch data"
        # )
        #
        # df["tdescore_hostfast"] = scores
        # mask = df["tdescore_hostfast"] > 0.00001
        #
        # df, proc_log = update_source_list(
        #     df, proc_log, mask, "TDEScore cuts with fast crossmatch data"
        # )
        #
        # df.sort_values(by="tdescore_hostfast", inplace=True, ascending=False)

        # Apply the second classifier which includes WISE data

        logger.info("Downloading WISE data")
        download_all(df.copy(), include_optional=False)

        logger.info("Combining all crossmatch data")
        full_df = combine_all_sources(df.copy(), save=False)

        scores, nan_mask = apply_classifier(full_df, "host", explain=False)

        df, proc_log = update_source_list(
            df, proc_log, ~nan_mask, "TDEScore nans with full host data"
        )

        df["tdescore_host"] = scores
        mask = df["tdescore_host"] > 0.0001

        df, proc_log = update_source_list(
            df, proc_log, mask, "TDEScore cuts with full crossmatch data"
        )

        df.sort_values(by="tdescore_host", inplace=True, ascending=False)


        # Download all the alert data up to the specific night
        logger.info(f"Downloading full lightcurve data using backend {ZTF_BACKEND}")
        passed_names = download_alert_data(
            df["ztf_name"], overwrite=True, t_max_jd=t_max_jd
        )

        mask = df["ztf_name"].isin(passed_names)

        df, proc_log = update_source_list(
            df, proc_log, mask, "Has lightcurve data"
        )

        # Download skyportal data (redshift, tns_name, classifications)
        df = download_from_skyportal(df)

        # Download legacy survey data (redshift - either specz or photz)
        download_legacy_survey_data(df.copy())

        # Now load the full lightcurve data, including the info from alerts
        combine_raw_source_data(df[["ztf_name"]])
        new_df = load_raw_sources()
        for col in new_df.columns:
            if col not in df.columns:
                df[col] = new_df[col]
        full_df = combine_all_sources(df, save=False)

        # Apply the third classifier which uses early lightcurve data
        logger.info("Analysing full lightcurve data")
        create_lightcurve_plots(full_df, base_output_dir)

        gp_output_dir = base_output_dir / "tdescore/gp"
        gp_output_dir.mkdir(parents=True, exist_ok=True)
        batch_analyse(
            full_df["ztf_name"],
            overwrite=True,
            include_text=False,
            base_output_dir=gp_output_dir,
            thermal_windows=[],
        )
        # Only run on the full lightcurve data
        batch_sncosmo(
            full_df["ztf_name"], overwrite=True,
            windows=[None],
        )

        logger.info("Combining full dataset")
        full_df = combine_all_sources(df, save=False)

        scores, nan_mask = apply_classifier(
            full_df, "infant", explain=True, shap_base_dir=shap_base_dir
        )

        df, proc_log = update_source_list(
            df, proc_log, ~nan_mask, "TDEScore nans with infant data"
        )

        df["tdescore_infant"] = scores
        df["tdescore"] = scores
        df["tdescore_best"] = "infant"

        df.sort_values(by="tdescore_infant", inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)

        logger.info(f"Assigning scores to {len(scores)} sources with later data")

        # From here we assign scores if data is available but don't cut on them
        full_df = combine_all_sources(df.copy(), save=False)
        scores, nan_mask = apply_classifier(
            full_df, "week", explain=True, shap_base_dir=shap_base_dir
        )
        df["tdescore_week"] = np.nan
        df.loc[~nan_mask, ["tdescore_week"]] = scores
        df.loc[~nan_mask, ["tdescore"]] = scores
        df.loc[~nan_mask, ["tdescore_best"]] = "week"

        best_windows = []

        for i, row in full_df.iterrows():
            windows = [x for x in THERMAL_WINDOWS if x is not None]
            windows = [x for x in windows if row["age"] > x]
            idx = len(windows)
            window = (THERMAL_WINDOWS + THERMAL_WINDOWS[-1:])[idx]
            best_windows.append(window)

        df["thermal_window"] = best_windows

        windows = []

        for window in THERMAL_WINDOWS:

            logger.info(f"Analysing thermal data for window {window}")

            mask = df["thermal_window"] == window

            if mask.sum() == 0:
                logger.info(f"No sources have thermal data for window {window}")
                continue

            logger.info(f"{sum(mask)} sources have thermal data for window {window}")

            batch_analyse_thermal(
                df["ztf_name"][mask],
                overwrite=True,
                base_output_dir=gp_output_dir,
                thermal_windows=[window],
            )
            # Run sncosmo on the data in the thermal window
            batch_sncosmo(
                full_df["ztf_name"][mask], overwrite=True,
                windows=[window],
            )

            windows.append(window)

        full_df = combine_all_sources(df, save=False)

        for window in windows:
            scores, nan_mask = apply_classifier(
                full_df, f"thermal_{window}", explain=True, shap_base_dir=shap_base_dir
            )
            df[f"tdescore_thermal_{window}"] = np.nan
            df.loc[~nan_mask, [f"tdescore_thermal_{window}"]] = scores
            df.loc[~nan_mask, ["tdescore"]] = scores
            df.loc[~nan_mask, ["tdescore_best"]] = f"thermal_{window}"

        full_df = combine_all_sources(df, save=False)
        high_noise_mask = pd.notnull(full_df["high_noise"]) & full_df["high_noise"]

        # From here we assign scores if data is available but don't cut on them
        full_df = combine_all_sources(df.copy(), save=False)
        scores, nan_mask = apply_classifier(
            full_df, "full", explain=True, shap_base_dir=shap_base_dir
        )
        df["tdescore_full"] = np.nan
        df.loc[~nan_mask, ["tdescore_full"]] = scores
        df.loc[~nan_mask, ["tdescore"]] = scores
        df.loc[~nan_mask, ["tdescore_best"]] = "full"
        df.loc[high_noise_mask, ["tdescore_full"]] = -1.0
        df.loc[high_noise_mask, ["tdescore"]] = -1.0

        df.sort_values(by="tdescore", inplace=True, ascending=False)

        export_to_db(df)

        download_all(df, include_optional=False)

        full_df = combine_all_sources(df, save=False)
        save_results(datestr=datestr, result_df=full_df)
        save_candidates(datestr=base_output_dir.name, candidates=df)

        mask = df["tdescore_best"].isin(["infant", "week"]) & (full_df["age"] > 14.0)
        df, proc_log = update_source_list(
            df, proc_log, ~mask, "Algorithmic cuts - age", export_db=False
        )

        logger.info(f"Applying age cut, leaving {len(df)} sources")

        mask = df["tdescore"] > 0.01
        df, proc_log = update_source_list(
            df, proc_log, mask, "TDEScore cuts", export_db=False
        )

        proc_log.append({
            "stage": "Final",
            "n_sources": len(df),
            "tdes": list(set([row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]]))
        })

        logger.info(f"Applying TDEScore cut, leaving {len(df)} sources")

        df.reset_index(drop=True, inplace=True)
        full_df = combine_all_sources(df, save=False)

        logger.info("Making HTML table")
        make_daily_html_table(full_df, base_output_dir, proc_log)

        export_to_skyportal(full_df)

        logger.info(df)


        # Create a subset of young transients
        mask = full_df["age"] < 14.0
        if mask.sum() == 0:
            logger.warning("No young transients found")
            return

        df = df[mask].copy().reset_index(drop=True)
        full_df = combine_all_sources(df, save=False)

        proc_log.append({
            "stage": "Algorithmic cuts - age",
            "n_sources": mask.sum(),
            "tdes": list(set([row["ztf_name"] for _, row in df.iterrows() if row["is_tde"]]))
        })
        make_daily_html_table(full_df, base_output_dir, proc_log, table_name=INFANT_HTML_NAME)

    except NoSourcesError:
        logger.warning("Terminated early due to lack of sources")

    update_archive(datestr)


