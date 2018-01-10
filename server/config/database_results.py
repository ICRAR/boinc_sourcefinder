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
Result database format
"""

from sqlalchemy import MetaData, Table, Column, String, Float, ForeignKey, BigInteger

DUCHAMP_METADATA = MetaData()

CATEGORY = Table('category', DUCHAMP_METADATA,
                 Column('id', BigInteger, primary_key=True),
                 Column('name', String)
                 )

CUBELET = Table('cubelet', DUCHAMP_METADATA,
                Column('id', BigInteger, primary_key=True),
                Column('name', String),
                Column('category_id', BigInteger, ForeignKey('category.id')),
                Column('ra', Float),
                Column('dec', Float),
                Column('freq', Float)
                )

PARAMETERS = Table('parameters', DUCHAMP_METADATA,
                   Column('id', BigInteger, primary_key=True),
                   Column('name', String),
                   Column('text', String)
                   )

SOURCE = Table('source', DUCHAMP_METADATA,
               Column('id', BigInteger, primary_key=True),
               Column('cubelet_id', BigInteger, ForeignKey('cubelet.id')),
               Column('parameters_id', BigInteger, ForeignKey('parameters.id')),
               Column('ra', Float),
               Column('dec', Float),
               Column('freq', Float),
               Column('w_20', Float),
               Column('w_50', Float),
               Column('w_freq', Float),
               Column('f_int', Float),
               Column('f_tot', Float),
               Column('f_peak', Float),
               Column('n_voxel', Float),
               Column('n_chan', Float),
               Column('n_spatpix', Float)
               )

result_database_def = {
    "CATEGORY": CATEGORY,
    "CUBELET": CUBELET,
    "PARAMETERS": PARAMETERS,
    "SOURCE": SOURCE
}
