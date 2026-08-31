from scantde.io import load_multinight_df
from scantde.utils.skyportal import SkyportalClient, get_followup
from scantde.utils import send_slack_message
from tqdm import tqdm
import pandas as pd
from tabulate import tabulate