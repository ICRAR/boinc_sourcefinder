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

# Manifest format:
# category, cube_file_name, frequency

import os
import argparse
from config import get_config
from sqlalchemy import create_engine, select, distinct, and_
from config.database_results import result_database_def as results_db

PARAMETERS = results_db["PARAMETERS"]
CATEGORY = results_db["CATEGORY"]
CUBELET = results_db["CUBELET"]
SOURCE = results_db["SOURCE"]


class AssetManifestExporter:
    """

    """
    class Asset:
        """

        """
        def __init__(self, category, cubename, frequency):
            """

            :param category:
            :param filename:
            :param frequency:
            """
            self.category = category
            self.cubename = cubename
            self.frequency = frequency

    def __init__(self, config):
        """

        """
        self.config = config
        self.assets = []

    def build_manifest(self, category):
        """

        :param category:
        :return:
        """

        engine = create_engine(self.config["BASE_DB_LOGIN"] + 'sourcefinder_results')
        connection = engine.connect()

        try:
            # Get all cubes in the desired category
            if category is None:
                # Do all cubes
                cubes = connection.execute(select([CUBELET]))
                print "No category specified. Running all cubes."
            else:
                cubes = connection.execute(select([CUBELET]).where(CUBELET.c.category_id == category))
                print "Only running cubes in category {0}".format(category)

            for cube in cubes:
                name = cube['name']
                print "Processing cube {0}".format(name)
                results = connection.execute(select([SOURCE]).where(SOURCE.c.cubelet_id == cube['id']))

                # Iterate over the results for each cube
                frequencies = set()
                for result in results:
                    frequency = result['freq']

                    if frequency not in frequencies:
                        self.assets.append(self.Asset(category, name, frequency))
                        frequencies.add(frequency)

        except Exception as e:
            print "Exception occurred: {0}".format(e.message)

        finally:
            connection.close()

    def save(self, filename):
        """

        :param filename:
        :return:
        """
        with open(filename, 'w') as f:
            for asset in self.assets:
                f.write("{0}, {1}, {2}".format(asset.category, asset.cubename, asset.frequency))



def parse_args():
    """
    Parse arguments for the program.
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=str, help='The file to write output to.')
    parser.add_argument('--category', type=str, help='The category to build a manifest for.')

    return vars(parser.parse_args())


if __name__ == "__main__":
    args = parse_args()
    category = args['category']
    exporter = AssetManifestExporter(get_config())

    exporter.build_manifest(args['category'])
    exporter.save(args['out'])
