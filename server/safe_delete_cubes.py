#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

"""
Deletes cubes from the sf_cubes directory safely once all runs are done processing the cube
"""
import os
import argparse
import hashlib

from config import get_config
from utils import form_wu_name
from sqlalchemy import create_engine, select


class CubeDeleteEntry:
    """

    """
    def __init__(self, cube_path):
        """
        :param cube_path:
        :return:
        """
        self.cube_path = cube_path
        self.progresses = []
        self.symlink_paths = []

    def can_delete(self):
        """
        :return:
        """
        for progress in self.progresses:
            if progress != 2:
                return False

        return True

    def delete(self):
        """
        :return:
        """
        for filename in self.symlink_paths:
            try:
                os.unlink(filename)
                # Boinc places an MD5 file in there too.
                os.remove(filename + ".md5")
            except Exception as e:
                print "Error unlinking {0}".format(e.message)

        try:
            os.remove(self.cube_path)
        except Exception as e:
            print "Error deleting {0}".format(e.message)

    def add(self, progress, path):
        """
        :param progress:
        :param path:
        :return:
        """
        self.progresses.append(progress)
        if os.path.exists(path):
            self.symlink_paths.append(path)

    def __str__(self):
        return "{0}: {1}, {2}".format(self.cube_path, self.progresses, self.symlink_paths)


class CubeDeleter:
    def __init__(self, config, app_name):
        """
        Initialise the CubeDeleter
        :param config: The config for the application
        """
        self.config = config
        self.engine = None
        self.connection = None
        self.download_dir = config["DIR_DOWNLOAD"]
        self.fanout = config["FANOUT"]
        self.app_name = app_name

    def get_download_path(self, filename):
        """
        Kevins code for hashing the download directory
        :param filename: Filename to get the download path for
        :return: Boinc download path for the provided filename
        """
        s = hashlib.md5(filename).hexdigest()[:8]
        x = long(s, 16)

        # Create the directory if needed
        hash_dir_name = os.path.join(self.download_dir, "%x" % (x % self.fanout))
        if os.path.isfile(hash_dir_name):
            pass
        elif os.path.isdir(hash_dir_name):
            pass
        else:
            os.mkdir(hash_dir_name)

        # "%s/%x/%s" % (self.download_dir, x % self.fanout, filename)
        return os.path.join(hash_dir_name, filename)

    def create_delete_entries(self, cubes):
        delete_entries = {}

        for cube in cubes:
            cube_name = cube["cube_name"]
            progress = cube["progress"]
            run_id = cube["run_id"]
            symlink = form_wu_name(self.app_name, run_id, cube_name) + ".tar.gz"
            cube_path = os.path.join(self.config["DIR_CUBE"], cube_name + ".fits.gz")

            symlink = self.get_download_path(symlink)

            if cube_name not in delete_entries:
                delete_entry = CubeDeleteEntry(cube_path)
                delete_entries[cube_name] = delete_entry
            else:
                delete_entry = delete_entries[cube_name]

            delete_entry.add(progress, symlink)

        return delete_entries.values()

    def __call__(self, dont_delete):
        CUBE = self.config["database"]["CUBE"]
        self.engine = create_engine(self.config["DB_LOGIN"])
        self.connection = self.engine.connect()

        try:
            # Look through all cubes
            cubes = [c for c in self.connection.execute(select([CUBE]))]
            print "Cube count: {0}".format(len(cubes))
            delete_entries = self.create_delete_entries(cubes)
            for entry in delete_entries:
                if entry.can_delete():
                    if dont_delete:
                        print "Would remove: {0}".format(entry)
                    else:
                        print "Deleting: {0}".format(entry.cube_path)
                        entry.delete()
        finally:
            self.connection.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--dont_delete', action='store_true', help="Don't delete, but instead list files that would be deleted", default=False)
    args = vars(parser.parse_args())

    return args

if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']
    dont_delete = arguments['dont_delete']

    print arguments

    config = get_config(app_name)

    deleter = CubeDeleter(config, app_name)

    exit(deleter(dont_delete))