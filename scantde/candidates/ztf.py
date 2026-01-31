#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to query ZTF candidates from Kowalski and save them to a file.

Adapted from the original code by Yuhan Yao.
"""
import time
import numpy as np
import pandas as pd
from pathlib import Path

import logging

from astropy.time import Time
from scantde.paths import get_input_cache

from tdescore.utils.kowalski import get_kowalski

logger = logging.getLogger(__name__)

BASE_ZTF_NAME = "ztf_alerts.dat"


def ztf_alerts_path(datestr: str) -> Path:
    """
    Get the ZTF alerts file for a given date.

    :param datestr: Date to get the ZTF alerts file for
    :return: Path to the ZTF alerts file
    """
    output_dir = get_input_cache(datestr)
    return output_dir / BASE_ZTF_NAME


def get_ztf_candidates(
    datestr: str,
) -> pd.DataFrame:
    """
    Get ZTF candidates for a given date.

    :param datestr: Date string in the format YYYYMMDD
    :return: DataFrame containing ZTF candidates
    """

    alerts_path = ztf_alerts_path(datestr)

    if alerts_path.exists():
        logger.info(f"ZTF alerts file already exists: {alerts_path}")
        return pd.read_csv(alerts_path)

    t_now = Time(datestr[:4] + "-" + datestr[4:6] + '-' + datestr[6:] + 'T15:00:00.0',
                format='isot').jd

    if t_now < 2458653.5:  # 2019-06-19
        logger.warning("Using old  data query settings, before drb was introduced.")
        # there is no drb for early data (from an old email: before June 19 2019)
        rb_cut = {'candidate.rb': {'$gt': 0.5}}
    else:
        # Anna's suggestion. That gives a 1.7% FNR and FPR.
        rb_cut = {'candidate.drb': {'$gt': 0.65}}

    # gt is greater than, lt is lower than
    q = {
        "query_type": "find",
        "query": {
            "catalog": "ZTF_alerts",
            "filter": {
                'candidate.jd': {'$gt': t_now - 1., '$lt': t_now},
                'candidate.isdiffpos': {'$in': ['1', 't']},
                'candidate.programid': {'$gt': 0},
                'candidate.ssdistnr': {'$lt': -1},
                **rb_cut
            },
            "projection": {
                "objectId": 1,
                "candidate.distpsnr1": 1,
                "candidate.distnr": 1,
                "candidate.sgscore1": 1,
                "candidate.programid": 1,
                "candidate.srmag1": 1,
                "candidate.sgmag1": 1,
                "candidate.simag1": 1,
                "candidate.szmag1": 1,
                "candidate.magnr": 1,
                "candidate.jd": 1,
                "candidate.fid": 1,
                "candidate.magpsf": 1,
                "candidate.sigmapsf": 1,
                "candidate.ra": 1,
                "candidate.dec": 1,
                "candidate.jdstarthist": 1,
                "candidate.jdendhist": 1,
                'candidate.ssdistnr': 1,
                'candidate.ndethist': 1,
                'candidate.neargaiabright': 1,
                'candidate.objectidps1': 1,
            }
        }
    }

    logger.info(f"Starting query for ZTF candidates on {datestr}")

    kowalski = get_kowalski()
    t1 = time.time()
    candidates = kowalski.query(query=q).get("default", {}).get("data", [])
    t2 = time.time()

    logger.info(f"Query took {t2-t1:.1f} seconds, found {len(candidates)} candidates")

    df = pd.DataFrame([val['candidate'] for val in candidates])

    names_all = np.array([val['objectId'] for val in candidates])
    df["name"] = names_all
    df["ztf_name"] = names_all

    df.to_csv(alerts_path, index=False)

    return df


