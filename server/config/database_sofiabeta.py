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
Sofia database format
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
               Column("id", Integer),
               Column("name", String),
               Column("x", Float),
               Column("y", Float),
               Column("z", Float),
               Column("x_geo", Float),
               Column("y_geo", Float),
               Column("z_geo", Float),
               Column("rms", Float),
               Column("rel", Float),
               Column("x_min", Float),
               Column("x_max", Float),
               Column("y_min", Float),
               Column("y_max", Float),
               Column("z_min", Float),
               Column("z_max", Float),
               Column("n_pix", Float),
               Column("n_los", Float),
               Column("n_chan", Float),
               Column("ra", Float),
               Column("dec", Float),
               Column("lon", Float),
               Column("lat", Float),
               Column("freq", Float),
               Column("velo", Float),
               Column("w20", Float),
               Column("w50", Float),
               Column("wm50", Float),
               Column("f_peak", Float),
               Column("f_int", Float),
               Column("f_wm50", Float),
               Column("ell_maj", Float),
               Column("ell_min", Float),
               Column("ell_pa", Float),
               Column("ell3s_maj", Float),
               Column("ell3s_min", Float),
               Column("ell3s_pa", Float),
               Column("kin_pa", Float),
               Column("bf_a", Float),
               Column("bf_b1", Float),
               Column("bf_b2", Float),
               Column("bf_c", Float),
               Column("bf_xe", Float),
               Column("bf_xp", Float),
               Column("bf_w", Float),
               Column("bf_chi2", Float),
               Column("bf_flag", Float),
               Column("bf_z", Float),
               Column("bf_w20", Float),
               Column("bf_w50", Float),
               Column("bf_f_peak", Float),
               Column("bf_f_int", Float),
               Column('workunit_name', String)
               )

CUBE_STATUS = Table('cube_status',
                    DUCHAMP_METADATA,
                    Column('cube_status_id', BigInteger, primary_key=True),
                    Column('status', String)
                    )

sofiabeta_database_def = {
    "RUN": RUN,
    "PARAMETER_FILE": PARAMETER_FILE,
    "PARAMETER_RUN": PARAMETER_RUN,
    "CUBE": CUBE,
    "RESULT": RESULT,
    "CUBE_STATUS": CUBE_STATUS
}
