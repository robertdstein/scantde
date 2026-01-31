import pandas as pd

def get_host_html(
    row: pd.Series
) -> str:
    """
    Generate a line of HTML with extinction corrections for a given row.

    :param row: Row containing 'ra' and 'dec' columns.
    :return: HTML string with extinction corrections.
    """
    try:
        host_line = (
            f"Host: mr: {row['host_r']:.1f}&nbsp;&nbsp; Mr: {row['host_Mr']:.1f} &nbsp;&nbsp;"
            f"[isdwarf={row['is_dwarf']}]&nbsp;&nbsp; | &nbsp;&nbsp; "
            f"redshift: {row['best_redshift']:.2f}&nbsp;&nbsp; "
        )

        if row['dist_mpc'] > 1000.:
            host_line += f"distance: {row['dist_mpc'] / 1000:.3G} Gpc &nbsp;&nbsp;"
        else:
            host_line += f"distance: {row['dist_mpc']:.3G} Mpc &nbsp;&nbsp;"
    except KeyError:
        host_line = "Host: Not available"
    return host_line