#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 16:52:58 2023

@author: yuhanyao
"""
import numpy as np
from astropy.time import Time
from astropy.table import Table


def make_page_links(name: str):
    """
    Generate links to various pages for a given source

    :param name: source name
    :return: html string
    """
    page_links = f"""
    [<a href="http://skipper.caltech.edu:8080/cgi-bin/growth/view_source.cgi?name={name}" target="_blank">Growth Marshal</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    [<a href="https://fritz.science/source/{name}" target="_blank">Fritz (Source Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    [<a href="https://fritz.science/alerts/ztf/{name}" target="_blank">Fritz (Alert Page)</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    [<a href="https://lasair.roe.ac.uk/object/{name}" target="_blank">Lasair</a>]
    &nbsp;&nbsp;&nbsp;&nbsp;
    """
    return page_links


# def print_pages_links(outputf, name):
#     outputf.write(make_page_links(name))
#
#
# def initiate_html_header(outputf, datestr, mytb, html_path):
#     ncand = len(mytb)
#     nknowntde = len(mytb[mytb["sec"] == 1])
#     tnow = Time(datestr[:4] + "-" + datestr[4:6] + '-' + datestr[6:] + 'T15:00:00.0',
#                 format='isot').jd
#
#     # html style borrowed from
#     # https://www.w3schools.com/howto/tryit.asp?filename=tryhow_css_two_columns
#     outputf.write('<!doctype html>')
#     outputf.write('<html>')
#     outputf.write('<head>')
#     outputf.write('<title>SOURCE MARSHAL</title>')
#     outputf.write('<style>\
#                   * {\
#                      box-sizing: border-box;\
#                   }\
#                 /* Create two equal columns that floats next to each other */\
#                 .column {\
#                          float: left;\
#                          width: 50%;\
#                          padding: 10px;\
#                          #height: 220px; /* Should be removed. Only for demonstration */\
#                 }\
#                 /* Clear floats after the columns */\
#                 .row:after {\
#                         content: "";\
#                         display: table;\
#                         clear: both;\
#                 }\
#                 /* Rounded corner definition */\
#                 #rcorners2 {\
#                     border-radius: 15px;\
#                     border: 2px solid #73AD21;\
#                     padding: 15px; \
#                     width: 80%;\
#                 }\
#                 table, th, td {\
#                     border: 1px solid black;\
#                     border-collapse: collapse;\
#                 }\
#                 th, td {\
#                     padding: 5px;\
#                 }\
#                 th {\
#                     text-align: right;\
#                 }\
#                 .boxed {\
#                     width: 300px;\
#                     border: 3px outset green;\
#                     text-align: center;\
#                     font-size: 20px;\
#                     margin: 10px;\
#                 } \
#                 </style>')
#     outputf.write('</head>')
#     outputf.write('<body>')
#
#     outputf.write('<font size="5" color="green">Candidate List %s</font>' % (datestr))
#     outputf.write('</br>')
#     outputf.write('</br>')
#
#     t1day = Time(tnow - 1, format="jd").datetime
#     t2day = Time(tnow + 1, format="jd").datetime
#     prv_day = str(t1day.year) + str(t1day.month).zfill(2) + str(t1day.day).zfill(2)
#     next_day = str(t2day.year) + str(t2day.month).zfill(2) + str(t2day.day).zfill(2)
#
#     outputf.write(
#         '<a href=%s target="_blank"><font size="3" color="green">Previous Day</font></a>' % (
#             html_path.replace(datestr, prv_day)))
#     outputf.write('&nbsp;&nbsp;&nbsp;&nbsp;')
#     outputf.write(
#         '<a href=%s target="_blank"><font size="3" color="green">Next Day</font></a>' % (
#             html_path.replace(datestr, next_day)))
#     outputf.write('&nbsp;&nbsp;&nbsp;&nbsp;')
#
#     # FILTER DESCRIPTION
#     outputf.write(
#         'This is the ZTF Massive Black Hole SWG Scanning Page for Nuclear TDE Candidates: %d Transients Passed, including %d known TDEs.' % (
#         ncand, nknowntde))
#
#     outputf.write('<hr style="width:50%;text-align:left;margin-left:0">')
#     return outputf
#
#
# Bell_2003_dat = np.array([
#     ['u-g', -0.221, 0.485, -0.099, 0.345, -0.053, 0.268, -0.105, 0.226, -0.128, 0.169,
#      -0.209, 0.133, -0.260, 0.123],
#     ['u-r', -0.390, 0.417, -0.223, 0.299, -0.151, 0.233, -0.178, 0.192, -0.172, 0.138,
#      -0.237, 0.104, -0.273, 0.091],
#     ['u-i', -0.375, 0.359, -0.212, 0.257, -0.144, 0.201, -0.171, 0.165, -0.169, 0.119,
#      -0.233, 0.090, -0.267, 0.077],
#     ['u-z', -0.400, 0.332, -0.232, 0.239, -0.161, 0.187, -0.179, 0.151, -0.163, 0.105,
#      -0.205, 0.071, -0.232, 0.056],
#     ['g-r', -0.499, 1.519, -0.306, 1.097, -0.222, 0.864, -0.223, 0.689, -0.172, 0.444,
#      -0.189, 0.266, -0.209, 0.197],
#     ['g-i', -0.379, 0.914, -0.220, 0.661, -0.152, 0.518, -0.175, 0.421, -0.153, 0.283,
#      -0.186, 0.179, -0.211, 0.137],
#     ['g-z', -0.367, 0.698, -0.215, 0.508, -0.153, 0.402, -0.171, 0.322, -0.097, 0.175,
#      -0.117, 0.083, -0.138, 0.047],
#     ['r-i', -0.106, 1.982, -0.022, 1.431, 0.006, 1.114, -0.052, 0.923, -0.079, 0.650,
#      -0.148, 0.437, -0.186, 0.349],
#     ['r-z', -0.124, 1.067, -0.041, 0.780, -0.018, 0.623, -0.041, 0.463, -0.011, 0.224,
#      -0.059, 0.076, -0.092, 0.019]
# ])
# Bell_2003_tab = Table(Bell_2003_dat,
#                       names=['color', 'a_g', 'b_g', 'a_r', 'b_r', 'a_i', 'b_i', 'a_z',
#                              'b_z', 'aJ', 'bJ', 'aH', 'bH', 'aK', 'bK'])
# Bell_2003_tab.add_index('color')
# solar_mag = dict(u=6.39, g=5.11, r=4.65, i=4.53, z=4.50)
#
#
# def get_logL_from_M(M, solar):
#     return (-0.4 * (M - solar))
#
#
# def get_Bell_2003_ML(G=None, R=None, I=None):
#     LU = LG = LR = LI = LZ = None
#     if G is not None and ~np.isnan(G) and G > -100:
#         logLG = get_logL_from_M(G, solar_mag['g'])
#     else:
#         logLG = None
#     if R is not None and ~np.isnan(R) and R > -100:
#         logLR = get_logL_from_M(R, solar_mag['r'])
#     else:
#         logLR = None
#     if I is not None and ~np.isnan(I) and I > -100:
#         logLI = get_logL_from_M(I, solar_mag['i'])
#     else:
#         logLI = None
#     logMstar = []
#     bands = [[G if G > -100 else None, 'g'], [R if R > -100 else None, 'r'],
#              [I if I > -100 else None, 'i']]
#     for logL, l in [[logLG, 'g'], [logLR, 'r'], [logLI, 'i']]:
#         for i, (c1, l1) in enumerate(bands):
#             for c2, l2 in bands[i:]:
#                 if l1 != l2 and c1 is not None and c2 is not None and logL is not None and ~np.isnan(
#                         c1) and ~np.isnan(c2) and ~np.isnan(logL):
#                     if l1 + '-' + l2 in Bell_2003_tab['color']:
#                         a_m = float(Bell_2003_tab.loc[l1 + '-' + l2]['a_' + l])
#                         b_m = float(Bell_2003_tab.loc[l1 + '-' + l2]['b_' + l])
#                         log_M_L = a_m + b_m * (c1 - c2)
#                         logMstar.append(log_M_L + logL)
#     return np.mean(logMstar)
#



