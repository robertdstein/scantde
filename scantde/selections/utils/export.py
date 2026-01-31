from unittest.mock import inplace

import pandas as pd

from tdescore.combine.parse import combine_all_sources

from scantde.io import save_candidates, save_results

from scantde.log import export_to_db
from scantde.selections.utils.tag_junk import tag_junk
from scantde.selections.utils.tag_dwarf import tag_dwarf
from scantde.utils.sync import rsync_data
from scantde.utils.cutouts import batch_create_cutouts
from scantde.selections.utils.relabel import relabel_fields


def export_results(df: pd.DataFrame, datestr: str, selection: str) -> pd.DataFrame:
    """
    Export the results of the junk tagging to the database and save them in the cache.
    Sends a notification to Slack with the results.

    :param df: DataFrame containing source data
    :param datestr: Date string for naming the output files
    :param selection: Selection name to use for the classifier (e.g. 'tdescore')
    :return: Final DataFrame with junk tags applied
    """

    full_df = combine_all_sources(df, save=False)

    thermal_df = relabel_fields(full_df)
    df = df.join(thermal_df, how="left", on="ztf_name")
    df["n_predets"] = df["ndethist"] - df["thermal_n_detections"]

    df = tag_dwarf(df)

    # Batch download the cutouts
    batch_create_cutouts(df)

    # Tag junk
    junk = tag_junk(df)
    df["is_junk"] = junk

    full_df = pd.concat([full_df, df], axis=1)
    full_df = full_df.loc[:, ~full_df.columns.duplicated()]

    # Export the results to the database, and caches
    export_to_db(df, selection=selection)
    save_results(datestr=datestr, selection=selection, result_df=full_df)
    save_candidates(datestr=datestr, selection=selection, candidates=df)
    # rsync_data(datestr=datestr)

    return full_df
