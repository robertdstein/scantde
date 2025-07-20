from pathlib import Path

import pandas as pd
from astropy.time import Time
from tqdm import tqdm

from scantde.html.header import base_html_header
from scantde.paths import base_html_dir
from tdescore.lightcurve.window import THERMAL_WINDOWS
from typing import Optional
from scantde.html.single import make_html_single
from scantde.log import ProcStage


import logging

logger = logging.getLogger(__name__)

TDESCORE_HTML_DIR = base_html_dir / "tdescore"


def format_processing_log(log: list[ProcStage]) -> str:
    """
    Function to format the processing log

    :param log: list[dict] Processing log
    :return: str Formatted log
    """

    log_df = pd.DataFrame([x.model_dump() for x in log])

    none_character = "/"

    missed_tdes = [[none_character]]

    for i in range(len(log_df) -1):
        prv_tdes = log_df["tdes"].iloc[i]
        nxt_tdes = log_df["tdes"].iloc[i+1]
        missed = list(set(prv_tdes) - set(nxt_tdes))
        missed_tdes.append(missed if len(missed) > 0 else [none_character])

    log_df["Missed TDEs"] = missed_tdes

    html = """
    <b>Processing Log:</b>
    <div>
    <table> 
    <tr>
        <th>Stage</th>
        <th>N candidates</th>
        <th>N TDEs</th>
        <th>Missed TDEs</th>
    </tr>
    """

    for i, row in log_df.iterrows():
        html += f"""
        <tr>
            <td>{row["stage"]}</td>
            <td text-align: center;>{row["n_sources"]}</td>
            <td text-align: center;>{len(row["tdes"])}</td>
            <td text-align: center;>{'&'.join(row["Missed TDEs"])}</td>
        </tr>
        """
    html += """
    </table>
    </div>
    """
    return html


def make_html_table(
    source_table: pd.DataFrame,
    html_header: str,
    base_output_dir: Path,
    selection: str,
    prefix: str = "",
    proc_log: Optional[list[ProcStage]] = None,
    classifiers: list[str] | None = None,
) -> str:
    """
    Function to generate HTML for a table of sources

    :param source_table: pd.DataFrame Table of sources
    :param html_header: str HTML header
    :param prefix: str Prefix for paths
    :param base_output_dir: Path Base output directory
    :param selection: str Selection type (e.g., 'tdescore')
    :param proc_log: list[ProcStage] Processing log
    :param classifiers: list[str] Classifiers to use
    :return: str HTML
    """

    proc_log_str = format_processing_log(proc_log) if proc_log is not None else ""

    html = html_header
    html += "<table>"

    for i, row in tqdm(source_table.iterrows(), total=len(source_table)):
        count_line = f"({i+1}/{len(source_table)})"
        html += make_html_single(
            row, base_output_dir=base_output_dir,
            prefix=prefix,
            selection=selection,
            count_line=count_line,
            classifiers=classifiers
        )

    html += f"""
    </table>
    <br>
    {proc_log_str}
    """

    return html


def make_daily_html_table(
    source_table: pd.DataFrame,
    output_dir: Path,
    base_output_dir: Path,
    selection: str,
    prefix: str = "",
    proc_log: Optional[list[ProcStage]] = None,
    classifiers: list[str] | None = None,
) -> str:
    """
    Function to generate HTML for a table of sources

    :param source_table: pd.DataFrame Table of sources
    :param output_dir: Path Output directory
    :param prefix: str Prefix for paths
    :param base_output_dir: Path Base output directory
    :param proc_log: list[dict] Processing log
    :param classifiers: list[str] Classifiers to use
    :return: str HTML
    """
    datestr = output_dir.name

    base_html_header(
        source_table,
    )

    # html_header = make_html_daily_header(datestr, source_table, output_path)
    html_header = base_html_header(
        source_table,
    )

    html = make_html_table(
        source_table, html_header, prefix=prefix,
        base_output_dir=base_output_dir, selection=selection,
        proc_log=proc_log, classifiers=classifiers
    )

    return html


# def make_archive_html_table(
#     source_table: pd.DataFrame,
#     classifier: str,
#     proc_log: Optional[list[dict]] = None,
#     archive_category: str = "archive",
# ) -> str:
#     """
#     Function to generate HTML for a table of sources
#
#     :param source_table: pd.DataFrame Table of sources
#     :param classifier: str Classifier
#     :param proc_log: list[dict] Processing log
#     :param archive_category: str Archive category
#     """
#
#     assert archive_category in ["archive", "recent"], \
#         f"Invalid archive category {archive_category}"
#
#     if archive_category == "archive":
#         output_path = archive_paths[classifier]
#     else:
#         output_path = recent_paths[classifier]
#
#     logger.info(f"Saving archive HTML page to {output_path}")
#
#     html_header = make_html_archive_header(classifier, source_table)
#
#     html = make_html_table(
#         source_table,
#         html_header=html_header, output_path=output_path, proc_log=proc_log,
#         # classifiers=[classifier]
#     )
#     return html

