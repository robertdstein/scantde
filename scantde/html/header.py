import pandas as pd


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
        source_line = (
            f"This is the ZTFbh scanning page for TDE Candidates: "
            f"{len(sources)} Transients Passed, "
            f"including {sources['is_tde'].sum()} known TDEs. "
        )

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
            Load Source Page: <input id="nameInput" name="name" value="{{ name or '' }}" style="width:200px;">
            <button type="submit">Search by Name</button>
        </form>
        <br>
        <form method="get" action="/search_by_date">
            Search by Date: <input type="date" name="date" value="{{ today }}">
            Lookback Days: <input type="number" name="lookback_days" min="1" value="{{ lookback_days or 1 }}" style="width:60px;">
            <label class="switch">
            Hide junk: <input type="checkbox" name="hide_junk" {% if hide_junk is not defined or hide_junk %}checked{% endif %}>
            </label>
            Scanning Mode:
            <select name="mode">
                <option value="all" {% if mode == 'all' %}selected{% endif %}>All</option>
                <option value="infant" {% if mode == 'infant' %}selected{% endif %}>Infant</option>
                <option value="non-infant" {% if mode == 'non-infant' %}selected{% endif %}>Non-Infant</option>
            </select>
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
    
    <p style="color:red;">{{{{ error }}}}</p>
    """
    )
    return html
