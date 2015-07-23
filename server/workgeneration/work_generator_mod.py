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
    return list_param_range


def generate_parameter_set(connection, run_id):
    """
    Generate the parameter set for the given run ID and database
    :param connections
    :param run_id
    """
    list_param_range = determine_param_values(connection, run_id)
    list_param_values = []

    parameter_value_generation(list_param_range, list_param_values)


def parameter_value_generation(param_range, param_values):

    '''
    :param param_range - this is a list of parameter_ids and corresponding parameter ranges
    :param_values - this is a list of parameter_ids and a corresponding value for that parameter ID
    '''

    LOGGER.info('Param range is ' + str(param_range) + 'Param value is ' + str(param_values))
    for params in param_range:
        if param_range is None:
            print 'inserting values into database'
            # insert values into the database
        else:
            LOGGER.info(params)
            p_id = params[0]
            p_range = str(params[1])
            LOGGER.info(p_range)
            if len(p_range) == 1:
                # this is just a single value, no need to loop
                value = p_range[0]
            elif len(p_range) == 2:
                # this is a range, so we go from the first to second value in incremental steps
                value1 = p_range[0]
                value2 = p_range[1]
                for value in range(value1, value2 + 1, 1):
                    test = 1
                    param_values
            elif len(p_range) > 2:
                # iterate through every value in the list
                # this is the threshold value
                i = 1

                # for value in p_range:
                # LOGGER.info('Current value is ' + value + 'for parameter_id ' + p_id)
                # remember these are ranges, so we need to go from initial to the final














