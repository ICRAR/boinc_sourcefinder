"""script that converts the datacube cuts (cubelets) into work units for the BOINC sourcefinder"""

import py_poinc 
import argparse 
from Boinc import configxml
from sqlalchemy.engine import create_engine

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--register', type=int, help = "the registration ID of the cubelet")
parser.add_argument('-l', '--limit', type=int, help = "only generate the N number of workunits (testing purposes)")
parser.add_argument('p', '--parameters', type=string, help "a (specific) parameter file to be sent with the workunit (testing)")




