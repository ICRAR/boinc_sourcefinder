"""
Connect to the BOINC database
"""
from sqlalchemy import Column, MetaData, BigInteger, Integer, String, Table

BOINC_METADATA = MetaData()

RESULT = Table('result',
               BOINC_METADATA,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('server_state', Integer),
               Column('workunitid', Integer),
               Column('appid', Integer),
               Column('name', String),
               Column('outcome', Integer),
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
