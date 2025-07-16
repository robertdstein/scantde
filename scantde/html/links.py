#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 16:52:58 2023

@author: yuhanyao
"""


def make_page_links(name: str) -> str:
    """
    Generate links to various pages for a given source

    :param name: source name
    :return: html string
    """
    page_links = f"""
    [<a href="https://fritz.science/source/{name}" target="_blank">Fritz (Source Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    [<a href="https://fritz.science/alerts/ztf/{name}" target="_blank">Fritz (Alert Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    """
    return page_links



