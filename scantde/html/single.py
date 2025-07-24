import pandas as pd
from pathlib import Path

from scantde.html.links import make_page_links

from tdescore.lightcurve.window import THERMAL_WINDOWS
from scantde.html.cutout import generate_cutout_html
from scantde.html.extinction import get_extinction_html

CLASSIFIERS = ["host", "infant", "week"] + [f"thermal_{x:.0f}" if x is not None else "thermal_all" for x in THERMAL_WINDOWS] + ["full"]


def make_html_single(
    row: pd.Series,
    base_output_dir: Path,
    selection: str,
    prefix: str = "",
    count_line: str = "",
    classifiers: list[str] | None = None,
    include_cutout: bool = False,
) -> str:
    """
    Function to generate HTML for a single source

    :param row: pd.Series Row of the source table
    :param count_line: str Line to add to the count
    :param selection: str Selection type (e.g., 'tdescore')
    :param prefix: str Prefix for paths
    :param base_output_dir: Path Output directory
    :param classifiers: list[str] Classifiers to use
    :param include_cutout: bool Whether to include cutout images
    :return: str HTML
    """

    if classifiers is None:
        classifiers = CLASSIFIERS

    night_prefix = f"{Path(prefix) / str(row["datestr"])}/"

    name = row["name"]

    lightcurve_ext = f"{night_prefix}lightcurves/{name}.png"
    lightcurve_path = base_output_dir / lightcurve_ext
    if lightcurve_path.exists():
        lightcurve_line = f'<img src="{lightcurve_ext}" height="240">'
    else:
        lightcurve_line = ""

    # Get appropriate shap path
    sub_dir = row["tdescore_best"]

    if str(sub_dir)[-1].isdigit():
        chunks = sub_dir.split("_")
        chunks[-1] = str(float(chunks[-1])) # Ensure the window is formatted correctly
        sub_dir = "_".join(chunks)

    elif sub_dir == "thermal_all":
        sub_dir = "thermal_None"

    shap_ext = f"{night_prefix}{selection}/shap/{sub_dir}/{name}.png"
    shap_path = base_output_dir / shap_ext
    if shap_path.exists():
        shap_line = f'<img src="{shap_ext}" height="220">'
    else:
        shap_line = ""

    # Get the line with classifier scores
    classifier_lines = []

    for classifier in classifiers[::-1]:
        clf_name = f"tdescore_{classifier}"

        new_line = f"{classifier}: N/A"

        if clf_name in row:
            if pd.notnull(row[clf_name]) & (row[clf_name] > 0.0):
                # Bold the current best
                if row["tdescore_best"] == classifier:
                    new_line = f"<b>{classifier}: {row[clf_name]:.3f} </b>"
                else:
                    new_line = f"{classifier}: {row[clf_name]:.3f}"

        classifier_lines.append(new_line)

    classifier_line = " | ".join(classifier_lines[::-1])

    name_line = (
        rf'<b>{count_line}</b> <a href="search_by_name?selection={selection}&name={name}"><b>'
        rf'<font size="3">{name}</font></b></a>'
        rf' [junk={row["is_junk"]}] [lcscore={row['tdescore_lc_score']:.2f}]&nbsp;&nbsp;&nbsp;&nbsp;'
    )

    name_line += (
        f"[Age: {row['age']:.0f} days] &nbsp;&nbsp;&nbsp;&nbsp; "
        f"RA: {row['ra']:.3f} &nbsp;&nbsp;&nbsp;&nbsp; "
        f"Dec: {row['dec']:.3f}  &nbsp;&nbsp;&nbsp;&nbsp;"
    )
    if prefix != "":
        name_line += f"Last Updated: {row['datestr']} &nbsp;&nbsp;&nbsp;&nbsp;"

    sky_class = row.get("skyportal_class", None)

    name_line += f"Skyportal Class: {sky_class}&nbsp;&nbsp;&nbsp;&nbsp;"

    if bool(row["is_tde"]):
        name_line += "This is a known TDE!&nbsp;&nbsp;&nbsp;&nbsp;"

    extinction_line = get_extinction_html(row)

    gp_ext = f"{night_prefix}gp/None/{name}.png"
    gp_path = base_output_dir / gp_ext

    gp_line = ""

    if gp_path.exists() & (row["tdescore_best"] == "full"):
        gp_line = f'<img src="{gp_ext}" height="250">'
    elif "thermal" in str(row["tdescore_best"]):
        window = row["thermal_window"]
        window = float(window) if pd.notnull(window) else None
        gp_thermal_ext = f"{night_prefix}gp_thermal/{window}/None/{name}.png"
        gp_line = f'<img src="{gp_thermal_ext}" height="250">'

    if include_cutout:
        cutout_line = generate_cutout_html(source=row, prefix=prefix)

        img_html = f"""
            <br>
            <div class="row">
            {cutout_line}{shap_line}
            </div>
            <div class="row">
            {lightcurve_line}
            {gp_line}
            </div>
        """

    else:
        img_html = f"""
            <div class="row", "text-align:center;">
            {lightcurve_line}
            {shap_line}
            {gp_line}
            </div>
        """

    html = f"""
    <div style="background-color:#FF5F1520;">
    {name_line}
    <a href=#top>[Back to Top]</a>
    <br>
    {extinction_line}
    <br>
    {make_page_links(row)}
    <br>
    {classifier_line}
    <br>
    </div>
    {img_html}
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """

    return html