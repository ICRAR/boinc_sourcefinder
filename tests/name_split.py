from boinc_sourcefinder.server.utils import split_wu_name, form_wu_name

if __name__ == "__main__":
    wu_name = "sofia_12_askap_cube_45_65_20"
    result_name = "duchamp_0_askap_cube_55_23_1_1_912930290"

    app_name, run_id, cube_name = split_wu_name(wu_name)

    print app_name
    print run_id
    print cube_name

    print form_wu_name(app_name, run_id, cube_name)