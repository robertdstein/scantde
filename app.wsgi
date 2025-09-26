import os
import sys
import tempfile
import site
import logging
import platform

logging.basicConfig(
    stream=sys.stderr, level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Python executable: %s", sys.executable)
logging.info("Python version: %s", sys.version)
logging.info(f"Platform version: {platform.python_version()}\n")
logging.info("sys.prefix: %s", sys.prefix)
logging.info("sys.path: %s", sys.path)

sys.path = ["/usr/lib64/python3.12"]
sys.path = ['/ursa/www/starshredder/scantde', '/usr/lib64/python312.zip', '/usr/lib64/python3.12', '/usr/lib64/python3.12/lib-dynload', '/usr/local/lib64/python3.12/site-packages', '/usr/local/lib/python3.12/site-packages', '/usr/lib64/python3.12/site-packages', '/usr/lib/python3.12/site-packages']

logging.info("sys.path: %s", sys.path)

import html
logging.info(f"Loaded html module from: {getattr(html, '__file__', None)}")


# --- Virtual environment setup ---
venv_path = "/ursa/www/starshredder/venv"
python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
site_packages = os.path.join(venv_path, "lib", python_version, "site-packages")

# Add virtualenv site-packages if not already present
if site_packages not in sys.path:
    #site.addsitedir(site_packages)
    sys.path.insert(0, site_packages)

logging.info("sys.path: %s", sys.path)

sys.prefix = venv_path

# --- Add project root to sys.path only once ---
project_root = "/ursa/www/starshredder/scantde"
#if project_root not in sys.path:
#    sys.path.insert(0, project_root)

logging.info("sys.path: %s", sys.path)

# --- Normalize sys.path to remove duplicates while keeping order ---
seen = set()
sys.path[:] = [p for p in sys.path if not (p in seen or seen.add(p))]

logging.info("sys.path: %s", sys.path)

# --- Logging for Apache error log ---
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.info("Python executable: %s", sys.executable)
logging.info("Python version: %s", sys.version)
logging.info("sys.prefix: %s", sys.prefix)
logging.info("sys.path: %s", sys.path)

# --- Environment variables ---
os.environ['HOME'] = project_root
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
os.environ["SCANTDE_DATA_DIR"] = "/n/ursa/www/starshredder/scantde_output"

from scantde.paths import tdescore_output_dir
os.environ["TDESCORE_DATA"] = str(tdescore_output_dir)

from dotenv import load_dotenv, find_dotenv
load_dotenv("/n/ursa/www/starshredder/scantde/.env")

logging.info(f"key: {os.getenv('SCANTDE_SECRET_KEY')}")

# --- Load the Flask app ---
from scantde.server import create_app
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = create_app()
logging.info(f"{app.url_map}")

application = DispatcherMiddleware(
    Flask("dummy_root"),
    {"/scantde": app}
)
