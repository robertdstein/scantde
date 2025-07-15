"""
Update the tdescore archive
"""

import logging

import pandas as pd

from scantde.selections.tdescore.io import load_candidates
from scantde.selections.tdescore.make_html import CLASSIFIERS, make_archive_html_table, TDESCORE_HTML_DIR
from tdescore.combine.parse import combine_all_sources
from astropy import units as u

from astropy.time import Time

from scantde.selections.tdescore.samples import export_selections

logger = logging.getLogger(__name__)


def update_archive(datestr: str):
    """
    Run the TDEScore integration for a given date
    """

    dates = sorted(x.stem for x in TDESCORE_HTML_DIR.glob("*") if x.is_dir())[::-1]

    t_now = Time(f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:8]}T00:00:00", format="isot", scale="utc")

    t_min = t_now - 31. * u.day

    min_datestr = f"{t_min.datetime.year}{t_min.datetime.month}{t_min.datetime.day}"

    names = []

    all_dfs = []

    for datestr in dates:
        try:
            df = load_candidates(datestr)
            mask = ~(df["ztf_name"].isin(names))
            df = df[mask]
            df["datestr"] = datestr
            names += list(df["ztf_name"])
            all_dfs.append(df)
        except FileNotFoundError:
            continue

    if len(all_dfs) == 0:
        logger.warning("No archival candidates found")
        return

    all_df = pd.concat(all_dfs)
    all_df = combine_all_sources(all_df, save=False)

    for classifier in CLASSIFIERS:
        logger.info(f"Applying classifier: {classifier}")

        classifier_name = f"tdescore_{classifier}"

        if classifier_name in all_df.columns:

            new = all_df.copy()
            mask = pd.notnull(new[classifier_name])
            new = new[mask]
            new = new.sort_values(by=classifier_name, ascending=False)
            new.reset_index(drop=True, inplace=True)

            make_archive_html_table(new, classifier=classifier, archive_category="archive")

            recent = new[new["datestr"].astype(int) >= int(min_datestr)]
            recent.reset_index(drop=True, inplace=True)

            make_archive_html_table(recent, classifier=classifier, archive_category="recent")

    export_selections(all_df)

