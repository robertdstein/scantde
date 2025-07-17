import pandas as pd
from pathlib import Path

from scantde.utils.tns import strip_tns_name

from scantde.html.links import make_page_links

from tdescore.lightcurve.extinction import get_extinction_correction, wavelengths, extra_wavelengths
from tdescore.lightcurve.window import THERMAL_WINDOWS

CLASSIFIERS = ["host", "infant", "week"] + [f"thermal_{x}" for x in THERMAL_WINDOWS] + ["full"]

all_wavelengths = wavelengths.copy()
all_wavelengths.update(extra_wavelengths)


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

    prefix = f"{Path(prefix) / str(row["datestr"])}/"

    name = row["ztf_name"]

    lightcurve_path = f"{prefix}tdescore/lightcurves/{name}.png"
    shap_path = f"{prefix}tdescore/shap/{row['tdescore_best']}/{name}.png"

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
        rf'<b>{count_line}</b> <a href="search_by_name?name={name}"><b><font size="3">{name}</font></b></a> &nbsp;&nbsp;&nbsp;&nbsp;'
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
        tns_name = strip_tns_name(tns_name)
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

    if gp_path.exists() & (row["tdescore_best"] == "full"):
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