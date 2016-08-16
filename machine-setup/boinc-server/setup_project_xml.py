import sys

PROJECT_NAME = sys.argv[1]
PROJECT_NICE_NAME = sys.argv[2]

def fix_project_xml(filename):

    good = False
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("<app>"):
                good = True
                break

    if good:
        return  # already has the app in it

    edit_line = 0
    with open(filename, 'rw') as f:
        edit_line += 1
        for line in f:
            if line.startswith("<boinc>"):
                # insert after this
                break

    with open(filename, 'rw') as f:

        file_data = f.readlines()

        print file_data[:edit_line]
        print file_data[edit_line:]

        out_data = []
        for line in file_data[:edit_line]:
            out_data.append(line)

        out_data.append("<app>\n")
        out_data.append("<name>{0}</name>\n".format(PROJECT_NAME))
        out_data.append("<user_friendly_name>{0}</user_friendly_name>\n".format(PROJECT_NICE_NAME))
        out_data.append("</app>\n")

        for line in file_data[edit_line:]:
            out_data.append(line)

    with open(filename, 'w') as f:
        f.writelines(out_data)

fix_project_xml("/home/ec2-user/projects/{0}/project.xml".format(PROJECT_NAME))