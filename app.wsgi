import os
import sys
import tempfile

os.environ['HOME'] = '/www/starshredder/scantde'
# stifle the wanring about MPLCONFIGDIR not being writable
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
sys.path.insert(0,"/n/www/starshredder/venv/lib/python3.11/site-packages")
sys.path.insert(0,"/n/www/starshredder/scantde")

from scantde.server import create_app

application = create_app()
