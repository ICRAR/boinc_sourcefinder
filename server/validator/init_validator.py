# Validation stage 1
# Checks one result and determines if it is valid
# Checks based on the following criteria:
#   Output must be a .tar.gz file
#   All required output files are present.
#   CSV header is correct
#   CSV hash is correct
#   Log files listing correct number of parameters processed

import os, sys, hashlib, csv, re, shutil

sys.path.append(os.path.abspath('/home/ec2-user/boinc_sourcefinder/server/'))

from utils.utilities import make_path, extract_tar
from shared import output_files, csv_valid_header, num_parameters

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

    return csv_hash == hash_file


def check_csv_header():
    # Check that the CSV header is correct
    csv_abs = os.path.join(outputs_path, output_files['csv'])
    with open(csv_abs) as f:
        csv_reader = csv.DictReader(f)
        headers = [f.strip() for f in csv_reader.fieldnames]

    return headers == csv_valid_header


def check_log_parameters():
    # Check that the log contains a duchamp run for each parameter
    log_abs = os.path.join(outputs_path, output_files['log'])
    with open(log_abs, 'r') as logfile:
        matches = re.findall("INFO:root:Running duchamp for supercube_run_[0-9]{5}\.par", logfile.read())

    return len(matches) >= num_parameters

check_functions = [(check_output_files, 'Missing one or more output files'),
                   (check_csv_header, 'CSV header is incorrect'),
                   (check_csv_hash, 'CSV hash is incorrect'),
                   (check_log_parameters, "Log file doesn't contain a run for each parameter")]


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


