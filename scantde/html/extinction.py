import pandas as pd

from scantde.selections.utils.extinction import ext_keys

def get_extinction_html(
    row: pd.Series
) -> str:
    """
    Generate a line of HTML with extinction corrections for a given row.

    :param row: Row containing 'ra' and 'dec' columns.
    :return: HTML string with extinction corrections.
    """
    extinction_line = "Extinction: "
    for f_name in ext_keys:
        extinction_line += f"{f_name.split('_')[-1]}: {row[f_name]:.2f} &nbsp;&nbsp;"
    return extinction_line