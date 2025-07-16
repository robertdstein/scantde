import pandas as pd
from pathlib import Path
from astropy.time import Time

def base_html_header(
    sources: pd.DataFrame,
    link_text: str = "",
) -> str:
    """
    Function to generate the base HTML header

    :param sources: pd.DataFrame Table of sources
    :param link_text: str | None Link text
    :return: str HTML
    """

    if len(sources) == 0:
        source_line = ""
    else:
        source_line = f"This is the ZTFbh scanning page for ML-selected TDE Candidates using tdescore: {len(sources)} Transients Passed, including {sources['is_tde'].sum()} known TDEs. "

    # if "datestr" in sources.columns:
    #     prefix = f'./'
    # else:
    #     prefix = "../"

    # archive_links = (
    #     f"""<br>
    # <div style="background-color:#FFE5B4;">
    # <b>Archive Pages:</b> <br>
    #     """
    # )
    #
    # for class_name, class_path in archive_paths.items():
    #     link = f"{prefix}{class_path.relative_to(TDESCORE_HTML_DIR)}"
    #     archive_links += f"""
    #     <a href={link} target="_blank">
    #     <font size="3" color="green">{class_name}</font></a>
    #     """
    # archive_links += " &nbsp;&nbsp;&nbsp;&nbsp; <br> </div>"
    #
    # archive_links += (
    #     f"""<br>
    # <div style="background-color:#FFE5B4;">
    # <b>Recents Pages:</b> <br>
    #     """
    # )
    #
    # for class_name, class_path in recent_paths.items():
    #     link = f"{prefix}{class_path.relative_to(TDESCORE_HTML_DIR)}"
    #     archive_links += f"""
    #     <a href={link} target="_blank">
    #     <font size="3" color="green">{class_name}</font></a>
    #     """
    # archive_links += " &nbsp;&nbsp;&nbsp;&nbsp; <br> </div> <br>"

    html = (
            """
        <!doctype html>
        <html>
        <head>
        <title>TDE Candidates</title>
        <style>\
          * {\
             box-sizing: border-box;\
          }\
        /* Create two equal columns that floats next to each other */\
        .column {\
                 float: left;\
                 width: 50%;\
                 padding: 10px;\
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
        <font size="5" color="green">TDE Candidate Portal</font>
        </br>
        </br>
        <hr style="height:2px;border-width:0;color:gray;background-color:gray">
        <div style="background-color:#F3E5AB;;">
        <font size="4">Search For Sources</font>
        </br>
        <form id="searchByNameForm" method="get" action="/search_by_name">
          Load Source Page: <input id="nameInput" name="name">
          <button type="submit">Search by Name</button>
        </form>
        <br>
        <form method="get" action="/search_by_date">
          Search Sources by Date: <input type="date" name="date" value="{{ today }}">
          Lookback Days: <input type="number" name="lookback_days" min="1" value="1">
          <button type="submit">Search by Date</button>
        </form>
        <br>
        </div>
        <hr style="height:2px;border-width:0;color:gray;background-color:gray">
        """
            + f"""
    {link_text}

    {source_line}
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


# def make_html_daily_header(
#     datestr: str,
#     sources: pd.DataFrame,
#     output_path: Path
# ) -> str:
#     """
#     Function to generate HTML header
#
#     :param datestr: str Date string
#     :param sources: pd.DataFrame Table of sources
#     :param output_path: Path Output path
#     :return: str HTML
#     """
#
#     tnow = Time(
#         f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:]}T15:00:00.0", format="isot"
#     ).jd
#     t1day = Time(tnow - 1, format="jd").datetime
#     t2day = Time(tnow + 1, format="jd").datetime
#     prv_day = str(t1day.year) + str(t1day.month).zfill(2) + str(t1day.day).zfill(2)
#     next_day = str(t2day.year) + str(t2day.month).zfill(2) + str(t2day.day).zfill(2)
#
#     prv_page = f"../{prv_day}/{output_path.name}"
#     next_page = f"../{next_day}/{output_path.name}"
#
#     link_text = (
#         f"""
#     <font size="5" color="green">Candidate List {datestr}</font>
#     </br>
#     </br>
#     <a href={prv_page} target="_blank"><font size="3" color="green">Previous Day</font></a>
#     &nbsp;&nbsp;&nbsp;&nbsp;
#     <a href={next_page} target="_blank"><font size="3" color="green">Next Day</font></a>
#     &nbsp;&nbsp;&nbsp;&nbsp;
#         """
#     )
#
#     html = base_html_header(sources, link_text)
#     return html


# def make_html_archive_header(
#     classifier: str,
#     sources: pd.DataFrame,
# ) -> str:
#     """
#     Create the HTML header for an archive page for a classifier
#
#     :param classifier: str Classifier
#     :param sources: pd.DataFrame Table of sources
#     """
#
#     link_text = f"""
#     <font size="5" color="green">Candidate List {classifier}</font>
#     </br>
#     </br>
#     """
#
#     html = base_html_header(sources, link_text)
#     return html