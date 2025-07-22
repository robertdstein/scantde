#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 16:52:58 2023

@author: yuhanyao
"""
import pandas as pd

from scantde.utils.tns import strip_tns_name



def make_page_links(row: pd.Series) -> str:
    """
    Generate links to various pages for a given source

    :param row: Pandas Series containing source information, including 'skyportal_tns_name'
    :return: html string
    """
    name = row["name"]
    page_links = f"""
    [<a href="https://fritz.science/source/{name}" target="_blank">Fritz (Source Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    [<a href="https://fritz.science/alerts/ztf/{name}" target="_blank">Fritz (Alert Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    """

    tns_name = row.get("skyportal_tns_name", None)

    if pd.notnull(tns_name):
        tns_name = strip_tns_name(tns_name)
        page_links += (
            f' [TNS: <a href="https://wis-tns.weizmann.ac.il/object/{tns_name}" target="_blank">'
            f"AT{tns_name}</a>] &nbsp;&nbsp;&nbsp;&nbsp;"
        )
    return page_links



