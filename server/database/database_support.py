"""A supporting sqlalchemy module based off Kevin's code for the database connections"""

from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, ForeignKey, BigInteger, Numeric

DUCHAMP_METADATA = MetaData()

RUN = Table('run',
            DUCHAMP_METADATA,
            Column('run_id', BigInteger, primary_key=True)
            )
PARAMATER = Table('parameter',
                  DUCHAMP_METADATA,
                  Column('parameter_id', BigInteger, primary_key=True),
                  Column('parameter_name', String)
                  )

PARAMATER_RANGE = Table('parameter_range',
                        DUCHAMP_METADATA,
                        Column('parameter_range_id', BigInteger, primary_key=True),
                        Column('parameter_string', String),
                        Column('parameter_id', BigInteger, ForeignKey('parameter.parameter_id')),
                        Column('run_id', BigInteger, ForeignKey('run.run_id'))
                        )

PARAMETER_GROUPING = Table('parameter_grouping',
                           DUCHAMP_METADATA,
                           Column('paramater_grouping_id', BigInteger, primary_key=Table),
                           Column('run_id', BigInteger, ForeignKey('run.run_id'))
                           )

PARAMATER_VALUES = Table('value',
                         DUCHAMP_METADATA,
                         Column('value_id', BigInteger, primary_key=True),
                         Column('value', Float),
                         Column('parameter_grouping_id', BigInteger,
                                ForeignKey('parameter_grouping.parameter_grouping_id'))
                         )

CUBE = Table('cube',
             DUCHAMP_METADATA,
             Column('cube_id', BigInteger, primary_key=True, autoincrement=True),
             Column('cube_name', String),
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