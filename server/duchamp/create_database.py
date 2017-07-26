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
import sys
from sqlalchemy import create_engine
from ..config import get_config

SQL = """
DROP SCHEMA IF EXISTS {0};
CREATE SCHEMA IF NOT EXISTS {0} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE {0} ;

# Runs
CREATE TABLE IF NOT EXISTS {0}.`run` (
  run_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;

# Parameter files
CREATE TABLE IF NOT EXISTS {0}.`parameter_file` (
  parameter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parameter_file_name VARCHAR(100),

  PRIMARY KEY (parameter_id)
) ENGINE = InnoDB;

# Link parameters to runs
CREATE TABLE IF NOT EXISTS {0}.`parameter_run` (
  parameter_run BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  run_id BIGINT UNSIGNED NOT NULL,
  parameter_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (parameter_run),

  FOREIGN KEY (run_id)
    REFERENCES {0}.`run`(`run_id`),

  FOREIGN KEY (parameter_id)
    REFERENCES {0}.`parameter_file` (`parameter_id`)
) ENGINE = InnoDB;

# Cube processing status
CREATE TABLE IF NOT EXISTS {0}.`cube_status` (
  cube_status_id BIGINT UNSIGNED NOT NULL,
  status VARCHAR(100) NOT NULL,

  PRIMARY KEY (cube_status_id)

) ENGINE = InnoDB;

INSERT INTO {0}.`cube_status` (cube_status_id, status) VALUES (0, 'Started');
INSERT INTO {0}.`cube_status` (cube_status_id, status) VALUES (1, 'WorkunitCreated');
INSERT INTO {0}.`cube_status` (cube_status_id, status) VALUES (2, 'ResultReceived');

# Cubes
CREATE TABLE IF NOT EXISTS {0}.`cube` (
  cube_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cube_name VARCHAR(2000) NOT NULL,
  progress  BIGINT UNSIGNED NOT NULL, #0 for registered, 1 for Work generated, 2 for assimilated
  ra FLOAT NOT NULL ,
  declin FLOAT NOT NULL ,
  freq FLOAT NOT NULL ,
  run_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`cube_id`),

  INDEX cube_run_index (`run_id` ASC),

  FOREIGN KEY (`run_id`)
  REFERENCES {0}.`run` (`run_id`),

  FOREIGN KEY (`progress`)
    REFERENCES {0}.`cube_status` (cube_status_id)
) ENGINE = InnoDB;

# Results
CREATE TABLE IF NOT EXISTS {0}.`result` (
  `result_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cube_id`   BIGINT UNSIGNED    NOT NULL,
  `parameter_id` BIGINT UNSIGNED NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,
  `RA` FLOAT NOT NULL,
  `DEC` FLOAT NOT NULL,
  `freq` FLOAT NOT NULL,
  `w_50` FLOAT NOT NULL,
  `w_20` FLOAT NOT NULL,
  `w_FREQ` FLOAT NOT NULL,
  `F_int` FLOAT NOT NULL,
  `F_tot` FLOAT NOT NULL,
  `F_peak` FLOAT NOT NULL,
  `Nvoxel` FLOAT NOT NULL,
  `Nchan` FLOAT NOT NULL,
  `Nspatpix` FLOAT NOT NULL,
  `workunit_name` VARCHAR(200),

  PRIMARY KEY (`result_id`),
  INDEX result_cube_index (`cube_id` ASC),

  FOREIGN KEY (`cube_id`)
  REFERENCES {0}.`cube` (`cube_id`),

  FOREIGN KEY (`parameter_id`)
    REFERENCES {0}.`parameter_file` (`parameter_id`),

  FOREIGN KEY (`run_id`)
  REFERENCES {0}.`run` (`run_id`)

)  ENGINE = InnoDB;
"""


def create_database(schema_name):
    config = get_config()

    engine = create_engine(config["BASE_DB_LOGIN"])
    connection = engine.connect()
    transaction = connection.begin()

    sql = SQL.format(schema_name)
    connection.execute(sql)

    transaction.commit()
    connection.close()


def destroy_database(schema_name):
    config = get_config()

    engine = create_engine(config["BASE_DB_LOGIN"])
    connection = engine.connect()
    transaction = connection.begin()

    sql = "DROP SCHEMA IF EXISTS {0};".format(schema_name)
    connection.execute(sql)

    transaction.commit()
    connection.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Not enough arguments"
        print "{0} [create | destroy] schema_name".format(sys.argv[0])
    else:
        if sys.argv[1] == "create":
            create_database(sys.argv[2])
        elif sys.argv[2] == "destroy":
            destroy_database(sys.argv[2])
