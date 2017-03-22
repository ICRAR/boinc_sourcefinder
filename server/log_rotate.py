#! /usr/bin/env python

# Open up the log_ip etc. folder
# Compress all of the .out files in there to .out_DATE_.gz

from config import filesystem
from utils.utilities import make_path
import os
import datetime
import gzip


def get_date_string():
    time = datetime.datetime.now()

    return "{0}_{1}_{2}_{3}".format(time.year, time.month, time.day, time.hour)


def main():
    folder = filesystem['log']

    make_path(filesystem['old_logs'])

    for f in os.listdir(folder):
        full_path = os.path.join(folder, f)

        compressed_name = f + get_date_string() + '.gz'
        with open(full_path, 'r') as log_file:
            file_data = log_file.read()

        with gzip.open(os.path.join(filesystem['old_logs'], compressed_name), 'wb') as compressed_file:
            compressed_file.write(file_data)

if __name__ == "__main__":
    main()
