"""A supporting sqlalchemy module based off Kevin's code for the database connections"""

from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, ForeignKey, BigInteger, Numeric

DUCHAMP_METADATA = MetaData()

RUN = Table('run',
            DUCHAMP_METADATA,
            Column('run_id', BigInteger, primary_key=True)
            )

PARAMETER_FILE = Table('parameter_file',
                       DUCHAMP_METADATA,
                       Column('parameter_id', BigInteger, primary_key=True),
                       Column('run_id', BigInteger, ForeignKey('run.run_id')),
                       Column('parameter_file', String)
                       )

CUBE = Table('cube',
             DUCHAMP_METADATA,
             Column('cube_id', BigInteger, primary_key=True, autoincrement=True),
             Column('cube_name', String),
             Column('progress', Integer),
             Column('ra', Float),
             Column('declin', Float),
             Column('freq', Float),
             Column('run_id', BigInteger, ForeignKey('run.run_id'))
             )

RESULT = Table('result',
               DUCHAMP_METADATA,
               Column('result_id', BigInteger, primary_key=True),
               Column('parameter_grouping_id', BigInteger, ForeignKey('parameter_grouping.parameter_grouping_id')),
               Column('cube_id', BigInteger, ForeignKey('cube.cube_id'))
               )

CUBE_USER = Table('cube_user',
                  DUCHAMP_METADATA,
                  Column('cube_user_id', BigInteger, primary_key=True),
                  Column('cube_id', Integer, ForeignKey('cube.cube_id'))
                  )