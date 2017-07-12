from sys import path
from os.path import dirname, realpath, abspath, join

# Ensure the 'server' directory is in our python path.
server_dir = dirname(abspath(realpath(join(__file__, ".."))))
path.append(server_dir)
