import pandas as pd
from scantde.utils.cutouts import get_cutout_path
from scantde.paths import base_html_dir
from pathlib import Path


def generate_ps1_html(
    source: pd.Series,
    prefix: str
) -> str:
    """
    Generate HTML for PS1 cutout of a source.

    :param source: Pandas Series containing source information, including 'name', 'ra', and 'dec'
    :return: HTML string for the PS1 cutout
    """

    ps1_cutout_path = get_cutout_path(source["name"], cutout_type="ps1")
    ps1_ext = Path(prefix) / ps1_cutout_path.relative_to(base_html_dir)

    ra, dec = source["ra"], source["dec"]

    if dec > 0:
        dec_sign = "+"
    else:
        dec_sign = "-"

    ps1_url = (f"http://ps1images.stsci.edu/cgi-bin/ps1cutouts"
               f"?pos={ra:.6f}{dec_sign}{abs(dec):.6f}&filter=color&filter=g&filter=r"
               f"&filter=i&filter=z&filter=y&filetypes=stack&auxiliary=data&size=240"
               f"&output_size=240&verbose=0&autoscale=99.500000")

    ps1_html = f'<a href = {ps1_url}><img src="{ps1_ext}" height="200"></a> \n'
    return ps1_html

def generate_ls_html(
    source: pd.Series,
    prefix: str
) -> str:
    """
    Generate HTML for Legacy Survey cutout of a source.

    :param source: Pandas Series containing source information, including 'name', 'ra', and 'dec'
    :param prefix: str Prefix for paths in the HTML
    :return: HTML string for the Legacy Survey cutout
    """

    ls_cutout_path = get_cutout_path(source["name"], cutout_type="legacy_survey")
    ls_ext = Path(prefix) / ls_cutout_path.relative_to(base_html_dir)

    ra, dec = source["ra"], source["dec"]

    if dec > 0:
        dec_sign = "+"
    else:
        dec_sign = "-"

    ls_url = (f"http://legacysurvey.org/viewer?ra={ra:.6f}&dec={dec_sign}{abs(dec):.6f}"
              f"&zoom=16")

    ls_html = f'<a href = {ls_url}><img src="{ls_ext}" height="200"></a> \n'

    return ls_html

def generate_cutout_html(
    source: pd.Series,
    prefix: str = "static/"
):
    """
    Generate HTML for cutouts of a source from PS1 and Legacy Survey.

    :param source: Pandas Series containing source information, including 'name', 'ra', and 'dec'
    :param prefix: str Prefix for paths in the HTML
    :return: HTML string for the cutouts
    """

    ps1_html = generate_ps1_html(source, prefix=prefix)
    ls_html = generate_ls_html(source, prefix=prefix)

    cutout_html = f"""
    {ps1_html}{ls_html}
    """

    return cutout_html

# generate_cutout_html(pd.Series({"name": "ZTF20abduida", "ra": 23.566844,  "dec": 30.611668}))


# # galaxy images
# images_line = ''
# images_ext = f"{prefix}tdescore/gal_images/"
# images_path = base_output_dir / images_ext
# images_path.mkdir(parents=True, exist_ok=True)
#
#
# # LegacySurvey
# fn = images_path / ("%s_ls.png" % name)
# if ~fn.exists():
#     #    https://www.legacysurvey.org/viewer/cutout.jpg?ra=115.2459&dec=16.5315&layer=ls-dr10-grz&pixscale=0.06
#     url = "https://www.legacysurvey.org/viewer/cutout.jpg?ra=%s&dec=%s&layer=ls-dr10-grz&zoom=16" % (
#     ra, dec)
#     r = requests.get(url)
#     plt.figure(figsize=(2.1, 2.1), dpi=120)
#     try:
#         plt.imshow(Image.open(io.BytesIO(r.content)))
#     except Exception:
#         logger.info(f"{name}: Legacy Survey image can not be shown...")
#         pass
#     plt.title("LegSurv DR10", fontsize=12)
#     plt.axis('off')
#     plt.tight_layout()
#     plt.savefig(fn, bbox_inches="tight")
#     plt.close()
# lslinkstr = "http://legacysurvey.org/viewer?" + \
#             "ra=%.6f&dec=%s%.6f" % (ra, decsign, abs(dec)) + \
#             "&zoom=16&layer=ls-dr10-grz"
# images_line += "<a href = %s>" % lslinkstr
# images_line += '<img src="%s" height="200">' % (fn.relative_to(base_output_dir))
# images_line += "</a> \n"