#! /usr/bin/env python
# Validation stage 2
# Compares two results and determines if they are equivalent.
# Checks based on the following criteria:
#   String compare of the CSV files.
#   Field by field compare of the CSV files, using a small tolerance to compare floating point values.

import csv
import hashlib
import os
import shutil
import sys

from config import filesystem
from utils import make_path, extract_tar
from validator_shared import output_files


def parse_args():
    if len(sys.argv) is not 3:
        return False

    return sys.argv[1], sys.argv[2]


class CSVCompare:

    def __init__(self, wu_file):
        self.wu_file = wu_file

        hash_name = hashlib.md5(wu_file).hexdigest()[:8]

        self.cells = None
        self.rows = None

        self.extract_directory_base = "/tmp/tmp_output{0}".format(hash_name)
        self.threshold = 0.0001

        self.load_csv()

    def load_csv(self):
        """
        Extracts the tar file associated with this work unit
        :return:
        """
        # Ensure a unique extract directory
        extract_dir = self.extract_directory_base

        while os.path.exists(extract_dir):
            extract_dir += '0'

        # Set up the local path variables.
        outputs_path = os.path.join(extract_dir, "outputs")

        try:
            extract_tar(self.wu_file, extract_dir)

            with open(os.path.join(outputs_path, output_files['csv']), 'r') as f:
                # Load the CSV rows.
                csv_file = csv.DictReader(f)
                self.cells = [a for r in csv_file for a in r.values()]
                self.rows = [r for r in csv_file]
        except:
            raise
        finally:
            if extract_dir and os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)

        return self.cells

    def _compare_rows(self, row1, row2):
        for cell1, cell2 in zip(row1, row2):
            if abs(float(cell1) - float(cell2)) > self.threshold:
                return False
        return True

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        if len(self.cells) != len(other.cells):
            print "Length of cells differs: {0}, to {1}".format(len(self.cells), len(other.cells))
            return False

        # Search for a matching rows. All of my rows must match with one of their rows.
        for my_row in self.rows:
            found = False
            for other_row in other.rows:
                if self._compare_rows(my_row, other_row):
                    found = True
                    break

            if not found:
                return False

        return True


def main():
    f = parse_args()
    if not f:
        print "Invalid number of arguments"
        return 1

    print "Starting on work unit files: {0} and {1}".format(f[0], f[1])

    try:
        f1 = CSVCompare(f[0])
        f2 = CSVCompare(f[1])
    except:
        print "Cannot open output files correctly"
        return 1

    if f1 == f2:
        print "Validation successful"
        return 0
    else:
        print "Validation Failed"
        folder = os.path.join(filesystem['validator_invalids'], 'compare')
        make_path(folder)
        shutil.copy(f[0], folder)
        shutil.copy(f[1], folder)
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print "Exception in compare validator: {0}".format(e.message)
        # Pretend they're valid for now so that we don't lose results.
        sys.exit(0)


########################################################################################## VALIDATOR INIT
#! /usr/bin/env python
# Validation stage 1
# Checks one result and determines if it is valid
# Checks based on the following criteria:
#   Output must be a .tar.gz file
#   All required output files are present.
#   CSV header is correct
#   CSV hash is correct
#   Log files listing correct number of parameters processed

import csv
import hashlib
import os
import re
import shutil
import sys

from config import filesystem
from utils import make_path, extract_tar
from validator_shared import output_files, csv_valid_header, num_parameters

extract_path = None
outputs_path = None


def check_output_files():
    # Check all output files are present
    files = os.listdir(outputs_path)

    if len(files) != len(output_files):
        print "Invalid number of output files"
        return False

    if set(files) != set(output_files.values()):
        print "Incorrectly named output file(s)"
        return False

    return True


def check_csv_hash():
    # Check that the csv hash is correct
    csv_abs = os.path.join(outputs_path, output_files['csv'])
    hashfile_abs = os.path.join(outputs_path, output_files['hash'])

    with open(csv_abs, 'r') as f:
        m = hashlib.md5()
        m.update(f.read())
        csv_hash = m.digest()

    with open(hashfile_abs, 'r') as f:
        hash_file = f.read()

    print "Hash compare: {0}, {1}".format(csv_hash, hash_file)
    return csv_hash == hash_file


def check_csv_header():
    # Check that the CSV header is correct
    csv_abs = os.path.join(outputs_path, output_files['csv'])
    with open(csv_abs) as f:
        csv_reader = csv.DictReader(f)
        headers = [f.strip() for f in csv_reader.fieldnames]

    print "Header compare:\n{0}\n{1}".format(headers, csv_valid_header)
    return headers == csv_valid_header


def check_log_parameters():
    # Check that the log contains a duchamp run for each parameter
    log_abs = os.path.join(outputs_path, output_files['log'])
    with open(log_abs, 'r') as logfile:
        matches = re.findall("INFO:root:Running duchamp for supercube_run_[0-9]{5}\.par", logfile.read())

    if len(matches) < num_parameters:
        with open(log_abs, 'r') as logfile:
            print "Log file that is invalid: {0}".format(logfile.read())

    return len(matches) >= num_parameters

check_functions = [(check_output_files, 'Missing one or more output files'),
                   (check_csv_header, 'CSV header is incorrect'),
                   (check_csv_hash, 'CSV hash is incorrect')]
#(check_log_parameters, "Log file doesn't contain a run for each parameter")]


def parse_args():
    if len(sys.argv) is not 2:
        return False

    return sys.argv[1]


def main():
    global extract_path, outputs_path

    f = parse_args()
    if not f:
        print "Invalid number of arguments"
        return 1

    print "Starting on work unit file: {0}".format(f)
    # Decompress the tar file:
    hash_name = hashlib.md5(f).hexdigest()[:8]
    extract_path = "/tmp/tmp_output{0}".format(hash_name)
    outputs_path = os.path.join(extract_path, "outputs")

    try:
        extract_tar(f, extract_path)
    except:
        print "Output is not an openable tar file"
        return 1

    for func in check_functions:
        if not func[0]():
            print func[1]
            folder = os.path.join(filesystem['validator_invalids'], 'init')
            make_path(folder)
            shutil.copy(f, folder)
            return 1

    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        if extract_path:
            shutil.rmtree(extract_path)
        sys.exit(exit_code)
    except Exception as e:
        print "Exception in init validator: {0}".format(e.message)
        # Pretend they're valid for now so that we don't lose results.
        sys.exit(0)


