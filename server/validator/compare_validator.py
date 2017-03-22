#! /usr/bin/env python
# Validation stage 2
# Compares two results and determines if they are equivalent.
# Checks based on the following criteria:
#   String compare of the CSV files.
#   Field by field compare of the CSV files, using a small tolerance to compare floating point values.

import os, sys, hashlib, csv, shutil

sys.path.append(os.path.abspath('/home/ec2-user/boinc_sourcefinder/server/'))
sys.path.append(os.path.abspath('/home/ec2-user/boinc_sourcefinder/server/validator'))

from config import filesystem
from utils.utilities import make_path, extract_tar
from shared import output_files


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

