#! /usr/bin/env python# -*- coding: utf-8 -*-##    ICRAR - International Centre for Radio Astronomy Research#    (c) UWA - The University of Western Australia#    Copyright by UWA (in the framework of the ICRAR)#    All rights reserved##    This library is free software; you can redistribute it and/or#    modify it under the terms of the GNU Lesser General Public#    License as published by the Free Software Foundation; either#    version 2.1 of the License, or (at your option) any later version.##    This library is distributed in the hope that it will be useful,#    but WITHOUT ANY WARRANTY; without even the implied warranty of#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU#    Lesser General Public License for more details.##    You should have received a copy of the GNU Lesser General Public#    License along with this library; if not, write to the Free Software#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,#    MA 02111-1307  USA#"""Generates all of the possible parameter file combinations for the given app.These are stored in the folder specified by "DIR_PARAM"."""import argparseimport osfrom config import get_configfrom utils import module_importfrom utils.logger import config_loggerfrom sqlalchemy.engine import create_enginefrom sqlalchemy import selectMODULE = "parameter_files_mod"LOG = config_logger(__name__)class ParameterFileGenerator:    def __init__(self, config):        self.config = config    def create_parameter_file_data(self):        LOG.error("Not implemented")        return {}    def create_parameter_files(self, file_data):        for filename, file_text in file_data:            name = os.path.join(self.parameter_path, filename)            with open(name, 'w') as new_file:                LOG.info("Saving parameter file: {0}".format(name))                new_file.write(file_text)    def register_parameter_files(self, file_data):        PARAMETER_FILE = self.database_def["PARAMETER_FILE"]        connection = None        transaction = None        try:            engine = create_engine(self.config["DB_LOGIN"])            connection = engine.connect()            transaction = connection.begin()            for filename, file_text in file_data:                check = connection.execute(select([PARAMETER_FILE]).where(PARAMETER_FILE.c.parameter_file_name == filename))                result = check.fetchone()                if not result:                    LOG.info("Registering file: {0}".format(filename))                    connection.execute(PARAMETER_FILE.insert(), parameter_file_name=filename)            transaction.commit()        except Exception as e:            transaction.rollback()            raise e        finally:            connection.close()    def __call__(self, add_to_db):        param = self.config["DIR_PARAM"]        self.parameter_path = param        self.database_def = self.config["database"]        if not os.path.exists(self.parameter_path):            os.makedirs(self.parameter_path)        try:            file_data = self.create_parameter_file_data()            self.create_parameter_files(file_data)            if add_to_db:                self.register_parameter_files(file_data)        except Exception:            LOG.exception("Create parameter files error")            return 1        return 0def parse_args():    parser = argparse.ArgumentParser()    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')    parser.add_argument('--add_to_db', action='store_true', help='Add the generated parameter files to the db.')    args = vars(parser.parse_args())    return argsif __name__ == "__main__":    arguments = parse_args()    app_name = arguments['app']    module = module_import(MODULE, app_name)    DerivedParameterFileGenerator = module.get_parameter_file_generator(ParameterFileGenerator)    parameter_generator = DerivedParameterFileGenerator(get_config(app_name))    exit(parameter_generator(arguments['add_to_db']))