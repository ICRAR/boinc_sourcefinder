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
"""
Duchamp database format
"""

from sqlalchemy import MetaData, Table, Column, Integer, String, Float, ForeignKey, BigInteger

DUCHAMP_METADATA = MetaData()

RUN = Table('run',
            DUCHAMP_METADATA,
            Column('run_id', BigInteger, primary_key=True)
            )

PARAMETER_FILE = Table('parameter_file',
                       DUCHAMP_METADATA,
                       Column('parameter_id', BigInteger, primary_key=True),
                       Column('parameter_file_name', String)
                       )

PARAMETER_RUN = Table('parameter_run',
                      DUCHAMP_METADATA,
                      Column('parameter_run', BigInteger, primary_key=True, autoincrement=True),
                      Column('run_id', BigInteger, ForeignKey('run.run_id')),
                      Column('parameter_id', BigInteger, ForeignKey('parameter_file.parameter_id')))

CUBE = Table('cube',
             DUCHAMP_METADATA,
             Column('cube_id', BigInteger, primary_key=True, autoincrement=True),
             Column('cube_name', String),
             Column('progress', Integer, ForeignKey('cube_status.cube_status_id')),
             Column('ra', Float),
             Column('declin', Float),
             Column('freq', Float),
             Column('run_id', BigInteger, ForeignKey('run.run_id'))
             )

RESULT = Table('result',
               DUCHAMP_METADATA,
               Column('result_id', BigInteger, primary_key=True, autoincrement=True),
               Column('cube_id', BigInteger, ForeignKey('cube.cube_id')),
               Column('parameter_id', BigInteger, ForeignKey('parameter_file.parameter_id')),
               Column('run_id', BigInteger, ForeignKey('run.run_id')),
               Column('RA', Float),
               Column('DEC', Float),
               Column('freq', Float),
               Column('w_50', Float),
               Column('w_20', Float),
               Column('w_FREQ', Float),
               Column('F_int', Float),
               Column('F_tot', Float),
               Column('F_peak', Float),
               Column('Nvoxel', Float),
               Column('Nchan', Float),
               Column('Nspatpix', Float),
               Column('workunit_name', String)
               )

CUBE_STATUS = Table('cube_status',
                    DUCHAMP_METADATA,
                    Column('cube_status_id', BigInteger, primary_key=True),
                    Column('status', String)
                    )

duchamp_database_def = {
    "RUN": RUN,
    "PARAMETER_FILE": PARAMETER_FILE,
    "PARAMETER_RUN": PARAMETER_RUN,
    "CUBE": CUBE,
    "RESULT": RESULT,
    "CUBE_STATUS": CUBE_STATUS
}
