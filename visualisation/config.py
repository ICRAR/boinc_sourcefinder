# database login
# image bucket
# active cubes path
# upload path

from configobj import ConfigObj

config_entries = [
    ("DB_LOGIN", ""),
    ("S3_IMAGE_BUCKET", "icrar.sourcefinder.images"),
    ("CUBES_PATH", "/home/ec2-user/visualisation_cubes"),
    ("UPLOAD_PATH", "/home/ec2-user/visualisation_upload")
]


def read_config(filename):
    """
    Reads the visualisation config from the provided file.
    :param filename: The config file name.
    :return: A dict containing the visualisation config.
    """
    config = {}
    config_obj = ConfigObj(filename)

    for item in config_entries:
        if item[0] in config_obj:
            config[item[0]] = config_obj[item[0]]
        else:
            config[item[0]] = item[1]

    return config

