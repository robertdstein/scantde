"""
Module for interfacing with SkyPortal
"""
from scantde.utils.skyportal.client import SkyportalClient, NoCredentialsError
from scantde.utils.skyportal.export import export_to_skyportal
from scantde.utils.skyportal.download import download_from_skyportal, get_skyportal_data
from scantde.utils.skyportal.followup import get_followup, get_spectra, batch_check_spec