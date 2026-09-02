"""
Module containing utility functions for the follow-up process.
"""

import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_sun
from astropy.time import Time

def get_best_airmass(ra_deg: float, dec_deg: float, site: str = "Palomar"):
    """
    Function to calculate the best airmass for a given RA, Dec, and observing site.

    :param ra_deg: Ra in degrees
    :param dec_deg: Dec in degrees
    :param site: Site name (default: "Palomar")
    :return: Airmass value (float) or NaN if the source is not observable
    """
    loc = EarthLocation.of_site(site)
    t0 = Time.now()
    times = t0 + np.arange(0, 24. * 60., 2.0) * u.minute
    frame = AltAz(obstime=times, location=loc)
    dark = get_sun(times).transform_to(frame).alt.deg < -18.0
    alt = SkyCoord(ra_deg * u.deg, dec_deg * u.deg).transform_to(frame).alt.deg
    best = np.where(dark, alt, -90.0).max()
    return 1.0 / np.cos(np.radians(90.0 - best)) if best > 0 else np.nan
