# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

import argparse
from sqlalchemy import create_engine
from config import get_config
from utils import module_import


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--action', type=str, choices=["create", "destroy"], required=True, help='The action to perform.')
    parser.add_argument('--schema', type=str, required=True, help="The schema name to use")
    args = vars(parser.parse_args())

    return args

if __name__ == "__main__":
    args = parse_args()
    app = args["app"]
    action = args["action"]
    schema = args["schema"]

    sql = ';'

    config = get_config(app)

    if action == "create":
        module = module_import("database_sql", app)
        sql = module.SQL.format(schema)
    elif action == "destroy":
        sql = "DROP SCHEMA IF EXISTS {0};".format(schema)

    engine = create_engine(config["BASE_DB_LOGIN"])
    connection = engine.connect()
    transaction = connection.begin()

    connection.execute(sql)

    transaction.commit()
    connection.close()
