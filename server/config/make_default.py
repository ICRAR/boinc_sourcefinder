"""
Makes a default configuration file

!!IF YOU MAKE A CHANGE HERE, MAKE SURE __init__.py IS CHANGED TOO!!
"""
from configobj import ConfigObj

if __name__ == "__main__":

    # Build a default config file

    config = ConfigObj()

    config.filename = 'duchamp.settings'

    config['databaseUserid'] = 'root'
    config['databasePassword'] = ''
    config['databaseHostname'] = 'localhost'
    config['databaseName'] = 'sourcefinder'

    config['boincDatabaseName'] = 'duchamp'

    config['paramDirectory'] = '/home/ec2-user/sf_parameters'
    config['cubeDirectory'] = '/home/ec2-user/sf_cubes'
    config['boincPath'] = '/home/ec2-user/projects/duchamp'

    config['wgThreshold'] = 500

    config.write()
