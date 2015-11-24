
import os
import sys

# Setup the Python Path as we may be running this via ssh
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))
sys.path.append(os.path.abspath(os.path.join(base_path, '../../../../boinc/py')))

import time
import assimilator
import gzip
import traceback
import datetime
from Boinc import boinc_db
from utils.logging_helper import config_logger
from config import DB_LOGIN
from sqlalchemy import create_engine
from sqlalchemy.sql import select

LOG = config_logger(__name__)
LOG.info('PYTHONPATH = {0}'.format(sys.path))

ENGINE = create_engine(DB_LOGIN)

