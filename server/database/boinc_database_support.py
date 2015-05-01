"""
Connect to the BOINC database
"""
from sqlalchemy import Column, MetaData, BigInteger, String, Table

BOINC_METADATA = MetaData()

RESULT = Table('result',
               BOINC_METADATA,
               Column('id', BigInteger, primary_key=True, autoincrement=True),
               Column('server_state', BigInteger),
               Column('workunitid', BigInteger),
               Column('appid', BigInteger),
               Column('name', String),
)

WORK_UNIT = Table('workunit',
                  BOINC_METADATA,
                  Column('id', BigInteger, primary_key=True, autoincrement=True),
                  Column('name', String),
                  Column('assimilate_state', BigInteger)
)

USER = Table('user',
             BOINC_METADATA,
             Column('id', BigInteger, primary_key=True, autoincrement=True),
             Column('name', String)
)
