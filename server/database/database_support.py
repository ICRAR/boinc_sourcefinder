"""A supporting sqlalchemy module based off Kevin's code for the database connections"""

from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, ForeignKey, BigInteger, Numeric

DUCHAMP_METADATA = MetaData()

RUN = Table('run',
            DUCHAMP_METADATA,
            Column('run_id', BigInteger, primary_key=True)
            )

PARAMETER_FILE = Table('parameter_file',
                       DUCHAMP_METADATA,
                       Column('parameter_file_id', BigInteger, primary_key=True),
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
             Column('progress', Integer),
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

CUBE_USER = Table('cube_user',
                  DUCHAMP_METADATA,
                  Column('cube_user_id', BigInteger, primary_key=True),
                  Column('cube_id', Integer, ForeignKey('cube.cube_id'))
                  )