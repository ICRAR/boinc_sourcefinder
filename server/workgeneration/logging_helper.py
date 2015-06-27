import logging
import logging.handlers

# Setup a small logging helper that prints to a general logging file for work generation
logging.basicConfig(filename='workgeneration.log', level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)



