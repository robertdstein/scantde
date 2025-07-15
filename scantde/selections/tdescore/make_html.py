from pathlib import Path

import pandas as pd
from astropy.time import Time
from tqdm import tqdm

from scantde.utils.html import make_page_links
from scantde.paths import base_html_dir
from tdescore.lightcurve.window import THERMAL_WINDOWS
from typing import Optional
from scantde.utils.tns import strip_tns_name
from tdescore.lightcurve.extinction import get_extinction_correction, wavelengths, extra_wavelengths

import logging

logger = logging.getLogger(__name__)

TDESCORE_HTML_DIR = base_html_dir / "tdescore"

TDESCORE_HTML_NAME = "tdescore_source_table.html"

INFANT_HTML_NAME = f"infant_{TDESCORE_HTML_NAME}"

CLASSIFIERS = ["host", "infant", "week"] + [f"thermal_{x}" for x in THERMAL_WINDOWS] + ["full"]

archive_paths = {
    classifier: TDESCORE_HTML_DIR / f"archive_{classifier}.html"
    for classifier in CLASSIFIERS
}

recent_paths = {
    classifier: TDESCORE_HTML_DIR / f"recent_{classifier}.html"
    for classifier in CLASSIFIERS
}

all_wavelengths = wavelengths.copy()
all_wavelengths.update(extra_wavelengths)


def base_html_header(
    sources: pd.DataFrame,
    link_text: str | None = None,
) -> str:
    """
    Function to generate the base HTML header

    :param sources: pd.DataFrame Table of sources
    :param link_text: str | None Link text
    :return: str HTML
    """

    if "datestr" in sources.columns:
        prefix = f'./'
    else:
        prefix = "../"

    archive_links = (
        f"""<br>
    <div style="background-color:#FFE5B4;">
    <b>Archive Pages:</b> <br>
        """
    )

    for class_name, class_path in archive_paths.items():
        link = f"{prefix}{class_path.relative_to(TDESCORE_HTML_DIR)}"
        archive_links += f"""
        <a href={link} target="_blank">
        <font size="3" color="green">{class_name}</font></a>
        """
    archive_links += " &nbsp;&nbsp;&nbsp;&nbsp; <br> </div>"

    archive_links += (
        f"""<br>
    <div style="background-color:#FFE5B4;">
    <b>Recents Pages:</b> <br>
        """
    )

    for class_name, class_path in recent_paths.items():
        link = f"{prefix}{class_path.relative_to(TDESCORE_HTML_DIR)}"
        archive_links += f"""
        <a href={link} target="_blank">
        <font size="3" color="green">{class_name}</font></a>
        """
    archive_links += " &nbsp;&nbsp;&nbsp;&nbsp; <br> </div> <br>"

    html = (
            """
        <!doctype html>
        <html>
        <head>
        <title>SOURCE MARSHAL</title>
        <style>\
          * {\
             box-sizing: border-box;\
          }\
        /* Create two equal columns that floats next to each other */\
        .column {\
                 float: left;\
                 width: 50%;\
                 padding: 10px;\
                 #height: 220px; /* Should be removed. Only for demonstration */\
        }\
        /* Clear floats after the columns */\
        .row:after {\
                content: "";\
                display: table;\
                clear: both;\
        }\
        /* Rounded corner definition */\
        #rcorners2 {\
            border-radius: 15px;\
            border: 2px solid #73AD21;\
            padding: 15px; \
            width: 80%;\
        }\
        table, th, td {\
            border: 1px solid black;\
            border-collapse: collapse;\
        }\
        th, td {\
            padding: 5px;\
        }\
        th {\
            text-align: right;\
        }\
        .boxed {\
            width: 300px;\
            border: 3px outset green;\
            text-align: center;\
            font-size: 20px;\
            margin: 10px;\
        } \
        </style>
        </head>
        <body>
    
        """
            + f"""
    {link_text}
    {archive_links}

    This is the ZTFbh scanning page for ML-selected TDE Candidates using tdescore: 
    {len(sources)} Transients Passed, including {sources['is_tde'].sum()} known TDEs. 
    <br>

    <br>
    <div style="background-color:#ffc0c0;">
    Disclaimer: tdescore will not select TDEs in milliquas-detected hosts, 
    or TDEs in galaxies without a WISE detection. <br>
    As more data is collected for a source, better tdescore classifiers can be used. <br>
    Look at the bolded classifier score to see which classifier is most reliable for each source.
    </div>    

    <hr style="width:50%;text-align:left;margin-left:0">
    """
    )
    return html


def make_html_daily_header(
    datestr: str,
    sources: pd.DataFrame,
    output_path: Path
) -> str:
    """
    Function to generate HTML header

    :param datestr: str Date string
    :param sources: pd.DataFrame Table of sources
    :param output_path: Path Output path
    :return: str HTML
    """

    tnow = Time(
        f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}T15:00:00.0", format="isot"
    ).jd
    t1day = Time(tnow - 1, format="jd").datetime
    t2day = Time(tnow + 1, format="jd").datetime
    prv_day = str(t1day.year) + str(t1day.month).zfill(2) + str(t1day.day).zfill(2)
    next_day = str(t2day.year) + str(t2day.month).zfill(2) + str(t2day.day).zfill(2)

    prv_page = f"../{prv_day}/{output_path.name}"
    next_page = f"../{next_day}/{output_path.name}"

    link_text = (
        f"""
    <font size="5" color="green">Candidate List {datestr}</font>
    </br>
    </br>
    <a href={prv_page} target="_blank"><font size="3" color="green">Previous Day</font></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href={next_page} target="_blank"><font size="3" color="green">Next Day</font></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
        """
    )

    html = base_html_header(sources, link_text)
    return html


def make_html_archive_header(
    classifier: str,
    sources: pd.DataFrame,
) -> str:
    """
    Create the HTML header for an archive page for a classifier

    :param classifier: str Classifier
    :param sources: pd.DataFrame Table of sources
    """

    link_text = f"""
    <font size="5" color="green">Candidate List {classifier}</font>
    </br>
    </br>
    """

    html = base_html_header(sources, link_text)
    return html


def make_html_single(
    row: pd.Series,
    base_output_dir: Path,
    prefix: str = "",
    count_line: str = "",
    classifiers: list[str] | None = None
) -> str:
    """
    Function to generate HTML for a single source

    :param row: pd.Series Row of the source table
    :param count_line: str Line to add to the count
    :param prefix: str Prefix for paths
    :param base_output_dir: Path Output directory
    :param classifiers: list[str] Classifiers to use
    :return: str HTML
    """

    if classifiers is None:
        classifiers = CLASSIFIERS

    if (prefix == "") & ("datestr" in row):
        prefix = f'{row["datestr"]}/'

    name = row["ztf_name"]

    lightcurve_path = f"{prefix}tdescore/lightcurves/{name}.png"
    shap_path = f"{prefix}tdescore/shap/infant/{name}.png"

    for key in classifiers:
        label = f"tdescore_{key}"
        if label in row:
            if not pd.isnull(row[f"tdescore_{key}"]):
                shap_path = f"{prefix}tdescore/shap/{key}/{name}.png"

    classifier_lines = []

    best = False
    for classifier in classifiers[::-1]:
        clf_name = f"tdescore_{classifier}"

        new_line = f"{classifier}: N/A"

        if clf_name in row:
            if pd.notnull(row[clf_name]) & (row[clf_name] > 0.0):
                # Bold the current best
                if not best:
                    new_line = f"<b>{classifier}: {row[clf_name]:.3f} </b>"
                    best = True
                else:
                    new_line = f"{classifier}: {row[clf_name]:.3f}"

        classifier_lines.append(new_line)

    classifier_line = " | ".join(classifier_lines[::-1])

    name_line = (
        rf'<b>{count_line}</b> <a href="#{name}"><b><font size="3">{name}</font></b></a> &nbsp;&nbsp;&nbsp;&nbsp;'
    )

    name_line += (
        f"[Age: {row['age']:.0f} days] &nbsp;&nbsp;&nbsp;&nbsp; "
        f"RA: {row['ra']:.3f} &nbsp;&nbsp;&nbsp;&nbsp; "
        f"Dec: {row['dec']:.3f}  &nbsp;&nbsp;&nbsp;&nbsp;"
    )
    if prefix != "":
        name_line += f"Last Updated: {row['datestr']} &nbsp;&nbsp;&nbsp;&nbsp;"

    tns_name = row["skyportal_tns_name"]
    if pd.notnull(tns_name):
        tns_name= strip_tns_name(tns_name)
        name_line += (
            f' (TNS: <a href="https://wis-tns.weizmann.ac.il/object/{tns_name}" target="_blank">'
            f"AT{tns_name}</a>) &nbsp;&nbsp;&nbsp;&nbsp;"
        )

    name_line += f"Skyportal Class: {row['skyportal_class']}&nbsp;&nbsp;&nbsp;&nbsp;"

    if bool(row["is_tde"]):
        name_line += "This is a known TDE!&nbsp;&nbsp;&nbsp;&nbsp;"

    extinction_line = "Extinction: "
    ra, dec = row["ra"], row["dec"]
    for f_name, wl in all_wavelengths.items():
        extinction = get_extinction_correction(ra, dec, [wl])
        extinction_line += f"{f_name}: {extinction[0]:.2f} &nbsp;&nbsp;"

    gp_ext = f"{prefix}tdescore/gp/None/{name}.png"
    gp_path = base_output_dir / gp_ext

    gp_thermal_ext = None

    for window in THERMAL_WINDOWS:
        new_thermal_ext = f"{prefix}tdescore/gp_thermal/{window}/None/{name}.png"
        gp_thermal_path = base_output_dir / new_thermal_ext
        key = f"tdescore_thermal_{window}"
        if key in row:
            if gp_thermal_path.exists() & pd.notnull(row[key]):
                gp_thermal_ext = new_thermal_ext
                break

    if gp_path.exists() & pd.notnull(row["tdescore_full"]) & ("full" in classifiers):
        gp_line = f'<img src="{gp_ext}" height="250">'
    elif gp_thermal_ext is not None:
        gp_line = f'<img src="{gp_thermal_ext}" height="250">'
    else:
        linear_path = base_output_dir / f"{prefix}tdescore/gp/{name}_linear.png"
        if linear_path.exists():
            gp_line = f'<img src="{prefix}tdescore/gp/{name}_linear.png" height="250">'
        else:
            gp_line = ""

    html = f"""
    <div style="background-color:#E8F8F5;">
    {name_line}
    <a href=#top>[Back to Top]</a>
    <br>
    {extinction_line}
    <br>
    {make_page_links(name)}
    <br>
    {classifier_line}
    </div>
    <br>

    <div class="row">
    <img src="{lightcurve_path}" height="240">
    <img src="{shap_path}" height="220">
    {gp_line}
    
    </div>
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """

    return html


def format_processing_log(log: list[dict]) -> str:
    """
    Function to format the processing log

    :param log: list[dict] Processing log
    :return: str Formatted log
    """

    log_df = pd.DataFrame(log)

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
    prefix: str = "",
    output_path: Path | None = None,
    base_output_dir: Path | None = None,
    proc_log: Optional[list[dict]] = None,
    classifiers: list[str] | None = None,
) -> str:
    """
    Function to generate HTML for a table of sources

    :param source_table: pd.DataFrame Table of sources
    :param html_header: str HTML header
    :param prefix: str Prefix for paths
    :param output_path: Path Output path
    :param base_output_dir: Path Base output directory
    :param proc_log: list[dict] Processing log
    :param classifiers: list[str] Classifiers to use
    :return: str HTML
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    proc_log_str = format_processing_log(proc_log) if proc_log is not None else ""

    html = html_header
    html += "<table>"

    if base_output_dir is None:
        base_output_dir = output_path.parent

    for i, row in tqdm(source_table.iterrows(), total=len(source_table)):
        count_line = f"({i+1}/{len(source_table)})"
        html += make_html_single(
            row, base_output_dir=base_output_dir,
            prefix=prefix,
            count_line=count_line,
            classifiers=classifiers
        )

    html += f"""
    </table>
    <br>
    {proc_log_str}
    """

    if output_path is not None:
        print(f"Saving HTML scanning page to {output_path}")

        with open(output_path, "w") as f:
            f.write(html)

    return html


def make_daily_html_table(
    source_table: pd.DataFrame,
    output_dir: Path,
    prefix: str = "",
    base_output_dir: Path | None = None,
    proc_log: Optional[list[dict]] = None,
    classifiers: list[str] | None = None,
    table_name: str = TDESCORE_HTML_NAME,
) -> str:
    """
    Function to generate HTML for a table of sources

    :param source_table: pd.DataFrame Table of sources
    :param output_dir: Path Output directory
    :param prefix: str Prefix for paths
    :param base_output_dir: Path Base output directory
    :param proc_log: list[dict] Processing log
    :param classifiers: list[str] Classifiers to use
    :param table_name: str Name of the HTML file
    :return: str HTML
    """
    datestr = output_dir.name

    output_path = TDESCORE_HTML_DIR / datestr / table_name

    html_header = make_html_daily_header(datestr, source_table, output_path)

    html = make_html_table(
        source_table, html_header, prefix=prefix,
        output_path=output_path, base_output_dir=base_output_dir, proc_log=proc_log, classifiers=classifiers
    )

    return html


def make_archive_html_table(
    source_table: pd.DataFrame,
    classifier: str,
    proc_log: Optional[list[dict]] = None,
    archive_category: str = "archive",
) -> str:
    """
    Function to generate HTML for a table of sources

    :param source_table: pd.DataFrame Table of sources
    :param classifier: str Classifier
    :param proc_log: list[dict] Processing log
    :param archive_category: str Archive category
    """

    assert archive_category in ["archive", "recent"], \
        f"Invalid archive category {archive_category}"

    if archive_category == "archive":
        output_path = archive_paths[classifier]
    else:
        output_path = recent_paths[classifier]

    logger.info(f"Saving archive HTML page to {output_path}")

    html_header = make_html_archive_header(classifier, source_table)

    html = make_html_table(
        source_table,
        html_header=html_header, output_path=output_path, proc_log=proc_log,
        # classifiers=[classifier]
    )
    return html

