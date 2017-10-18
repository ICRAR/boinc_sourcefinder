import csv
import os

RESULT_COLUMNS = [
    "id",
    "name",
    "x",
    "y",
    "z",
    "x_geo",
    "y_geo",
    "z_geo",
    "rms",
    "rel",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "n_pix",
    "n_los",
    "n_chan",
    "ra",
    "dec",
    "lon",
    "lat",
    "freq",
    "velo",
    "w20",
    "w50",
    "wm50",
    "f_peak",
    "f_int",
    "f_wm50",
    "ell_maj",
    "ell_min",
    "ell_pa",
    "ell3s_maj",
    "ell3s_min",
    "ell3s_pa",
    "kin_pa",
    "bf_a",
    "bf_b1",
    "bf_b2",
    "bf_c",
    "bf_xe",
    "bf_xp",
    "bf_w",
    "bf_chi2",
    "bf_flag",
    "bf_z",
    "bf_w20",
    "bf_w50",
    "bf_f_peak",
    "bf_f_int"
]

print "Storing data..."

with open("data_collection.csv") as open_csv_file:

    has_results = not open_csv_file.read().startswith("No sources")
    open_csv_file.seek(0)

    if has_results:
        csv_reader = csv.DictReader(open_csv_file)

        try:
            for row in csv_reader:

                table_insert = {column: (row[column] if row[column] != "null" else None) for column in RESULT_COLUMNS if column in row}
                table_insert["cube_id"] = 0
                table_insert["parameter_id"] = int(row['parameter_number'])
                table_insert["run_id"] = 1
                table_insert["workunit_name"] = "some_name"

                print table_insert

            print 'Successfully loaded work unit {0} in to the database'.format("some_name")

        except Exception as e:
            print 'Exception while loading CSV in to the database {0}'.format(e.message)
    else:
        print "No sources in result."

