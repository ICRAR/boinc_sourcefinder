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
BOINC database format
"""
from sqlalchemy import Column, MetaData, BigInteger, Integer, String, Table

BOINC_METADATA = MetaData()

RESULT = Table('result',
               BOINC_METADATA,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('server_state', Integer),
               Column('client_state', Integer),
               Column('workunitid', Integer),
               Column('appid', Integer),
               Column('name', String),
               Column('outcome', Integer),
               Column('xml_doc_in', String)
)

WORK_UNIT = Table('workunit',
                  BOINC_METADATA,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('name', String),
                  Column('assimilate_state', Integer),
                  Column('canonical_resultid', Integer),
)

USER = Table('user',
             BOINC_METADATA,
             Column('id', BigInteger, primary_key=True, autoincrement=True),
             Column('name', String)
)

boinc_database_def = {
    "RESULT": RESULT,
    "WORK_UNIT": WORK_UNIT,
    "USER": USER
}
