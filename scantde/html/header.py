import pandas as pd


def base_html_header(
    sources: pd.DataFrame,
) -> str:
    """
    Function to generate the base HTML header

    :param sources: pd.DataFrame Table of sources
    :return: str HTML
    """

    if len(sources) == 0:
        source_line = ""
    else:
        source_line = (
            f"Search Results: "
            f"{len(sources)} Transients Passed, "
            f"including {sources['is_tde'].sum()} known TDEs. <br>"
            '<hr style="height:2px;border-width:0;color:gray;background-color:gray">'
        )

    html = (
            """
        <!doctype html>
        <html>
        <head>
        <title>TDE Candidates</title>
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
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
        <img src="{{ url_for('static', filename='scantde_logo.png') }}" alt="Logo" style="display:block; margin:auto; max-width:100px;">
        <div style="height:0.5em;"></div>
        <div style="text-align:center;">
          <font size="5" color="#FF5F15">TDE Candidate Portal</font>
        </div>
        <hr style="height:2px;border-width:0;color:gray;background-color:gray">
        <div style="background-color:#FF5F1550">
        <font size="4"><b>Search For Sources</b></font>
        </br>
        <br>
        TDE Selection:
        <select id="selectionDropdown" name="selectionDropdown">
            <option value="tdescore" {% if selection == 'tdescore' %}selected{% endif %}>tdescore (classic)</option>
            <option value="tdescore_nohostinfo" {% if selection == 'tdescore_nohostinfo' %}selected{% endif %}>tdescore (no host info)</option>
            <option value="tdescore_offnuclear" {% if selection == 'tdescore_offnuclear' %}selected{% endif %}>tdescore (off-nuclear)</option>
        </select>
        <br>
        <br>
        <span id="selectionText" style="margin-left:20px; font-style:italic;"></span>
        <br>
        <br>
        <form id="searchByNameForm" method="get" action="/search_by_name">
            <input type="hidden" name="selection" id="selectionByName">
            Load Source Page: <input id="nameInput" name="name" value="{{ name or '' }}" style="width:200px;">
            <button type="submit">Search by Name</button>
        </form>
        <br>
        <form method="get" action="/search_by_date">
            <input type="hidden" name="selection" id="selectionByDate">
            Search by Date: <input type="date" name="date" value="{{ today }}">
            Lookback Days: <input type="number" name="lookback_days" min="1" value="{{ lookback_days or 1 }}" style="width:60px;">
            <label class="switch">
            Min Score: <input type="number" name="min_score" min="0.0" max="1.0" step="0.01" value="{{ min_score | default(0.01, true) }}" style="width:60px;">
            <label class="switch">
            Hide junk: <input type="checkbox" name="hide_junk" {% if hide_junk is not defined or hide_junk %}checked{% endif %}>
            </label>
            <label class="switch">
            |  Show Cutouts: <input type="checkbox" name="show_cutout" {% if show_cutout %} checked {% endif %}>
            </label>
            |  Scanning Mode:
            <select name="mode">
                <option value="all" {% if mode == 'all' %}selected{% endif %}>All</option>
                <option value="infant" {% if mode == 'infant' %}selected{% endif %}>Infant (<7d)</option>
                <option value="has-lc" {% if mode == 'has-lc' %}selected{% endif %}>Has GP fit</option>
                <option value="bright" {% if mode == 'bright' %}selected{% endif %}>Bright (m<19)</option>
                <option value="nearby" {% if mode == 'nearby' %}selected{% endif %}>Nearby (<150 Mpc)</option>
                <option value="dwarf" {% if mode == 'dwarf' %}selected{% endif %}>Dwarf (Mr<-19) | (mr>22)</option>
                <option value="junk" {% if mode == 'junk' %}selected{% endif %}>Junk</option>
                <option value="blue" {% if mode == 'blue' %}selected{% endif %}>Blue (T>10^4K)</option>
                <option value="red" {% if mode == 'red' %}selected{% endif %}>Red (T<5K)</option>
            </select>
            <button type="submit">Search by Date</button>
        </form>
        
        <script>
            // Set hidden inputs on page load and dropdown change
            function updateSelectionInputs() {
                var value = document.getElementById('selectionDropdown').value;
                document.getElementById('selectionByName').value = value;
                document.getElementById('selectionByDate').value = value;
                
                // Update text based on selection
                var text = "";
                if (value === "tdescore") {
                    text = "tdescore (classic) classifier uses LC, nuclearity and host info to classify TDEs. It will not classify sources which are missing host parameters, e.g. if the host is not WISE-detected.";
                } else if (value === "tdescore_nohostinfo") {
                    text = "tdescore (no host info) classifier uses only LC and nuclearity for classification. Probable AGN in WISE (W1-W2 > 0.7) are removed manually, but host info is not given to the classifier for scoring.";
                } else if (value === "tdescore_offnuclear") {
                    text = "tdescore (off-nuclear) classifier uses only LC for classification. It will classify everything.";
                }
                document.getElementById('selectionText').textContent = text;
            }
            document.getElementById('selectionDropdown').addEventListener('change', updateSelectionInputs);
            window.onload = updateSelectionInputs;
        </script>
        <br>
        </div>
        <hr style="height:2px;border-width:0;color:gray;background-color:gray">
        """
            + f"""
    <div>
    As more data is collected for a source, better tdescore classifiers can be used. <br>
    Look at the bolded classifier score to see which classifier is most reliable for each source.
    </div>
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    {source_line}
    
    <p style="color:red;">{{{{ error }}}}</p>
    """
    )
    return html
