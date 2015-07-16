# Helper file for the work generator

import os
from database.database_support import PARAMATER, PARAMATER_RANGE, PARAMATER_VALUES, PARAMETER_GROUPING
from sqlalchemy.engine import create_engine
from sqlalchemy import select, insert, and_, func
from logging_helper import config_logger

LOGGER = config_logger(__name__)
LOGGER.info("work_generator_mod.py")


def determine_param_values(connection, run_id):
    """
    Goes into the database and finds all the required values needed to determine each separate parameter grouping
    """
    LOGGER.info("Starting parameter generation")
    param_list = []
    param_id = []
    param_range = []


    # used to compare the names of the parameters with what is in the other areas of the database
    param = connection.execute(select([PARAMATER]))
    for row in param:
        param_list.append(row[1])
        retval = connection.execute(select([PARAMATER.c.parameter_id]).where(PARAMATER.c.parameter_name == row[1]))
        for row2 in retval:
            param_no = str(row2[0])
            param_id.append(param_no)
            LOGGER.info('Parameter ' + row[1] + ' has parameter_id ' + param_no)
            retval = connection.execute(
                select([PARAMATER_RANGE.c.parameter_string]).where(PARAMATER_RANGE.c.parameter_id == param_no))
            for row3 in retval:
                param_range.append(row3[0])
                LOGGER.info('Range is ' + row3[0])


    i = 0
    list_param_range = []
    for param in param_id:
        list_param_range.append((param, param_range[i]))
        i += 1

face

def generate_parameter_set(connection, run_id):
    """
    Generate the parameter set for the given run ID and database
    :param connection
    :param run_id
    """
    list_param_range = determine_param_values(connection, run_id)




