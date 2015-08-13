__author__ = '21298244'

# Helper file for the work generator

import os
from sqlalchemy.engine import create_engine
from sqlalchemy import select, insert, and_, func
from logging_helper import config_logger

LOGGER = config_logger(__name__)
LOGGER.info("work_generator_mod.py")



