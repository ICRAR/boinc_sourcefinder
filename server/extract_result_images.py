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
import os
import errno
import tarfile
import argparse
from astropy.io import fits
from scipy.misc import imsave
from multiprocessing import JoinableQueue, Process, get_logger

LOGGER = get_logger()
TEMP_FOLDER = '/scratch/sam/image_extract_temp'


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Consumer(Process):
    """
    A class to process jobs from the queue
    """

    def __init__(self, queue):
        Process.__init__(self)
        self._queue = queue

    def run(self):
        """
        Sit in a loop
        """
        while True:
            LOGGER.info('Getting a task')
            next_task = self._queue.get()
            if next_task is None:
                # Poison pill means shutdown this consumer
                LOGGER.info('Exiting consumer')
                self._queue.task_done()
                return
            LOGGER.info('Executing the task')
            # noinspection PyBroadException
            try:
                next_task()
            except:
                LOGGER.exception('Exception in consumer')
            finally:
                self._queue.task_done()


class ImageExtractJob:
    path_map = {
        0: "/mnt/hidata/dingo/skynet/v1/skynet_cubelets",
        1: "/mnt/hidata/dingo/skynet/v1/skynet_cubelets",
        2: "/mnt/hidata/dingo/skynet_v2/skynet_cubelets"
    }

    cube_file_prefix = "askap_cube_"

    def __init__(self, asset):
        self.asset = asset

    def _get_cube_path(self):
        path = self.path_map[self.asset.category]

        cubename = self.asset.cubename[len(self.cube_file_prefix):]
        number = cubename[:cubename.find('_')]

        return os.path.join(path, 'cubelets{0}'.format(number), "{0}.fits".format(self.asset.cubename))

    def __call__(self):
        """

        :return:
        """

        # Form a path to the cube
        path = self._get_cube_path()
        # Open it
        hdulist = fits.open(path, memmap=True)
        # Convert the specified layer to a PNG image
        layer = hdulist[0]
        start = float(layer.header["CRVAL3"])
        delta = float(layer.header["CDELT3"])
        index = int((self.asset.frequency - start) / delta)

        data = layer.data[index]  # Pull out that layer

        # Save the PNG image with a unique name into the TEMP_FOLDER



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
        self.frequency = float(frequency)


def build_jobs(manifest, queue):
    """
    Parse out entries from the manifest
    :param manifest:
    :param queue:
    :return:
    """
    with open(manifest, 'r') as f:
        for line in f:
            # One per line, split by commas.
            elements = line.split(',')
            queue.put(ImageExtractJob(Asset(elements[0].trim(), elements[1].trim(), elements[2].trim())))


def compress_output(out_file):
    """
    Compress the images in the output folder together
    :param out_file:
    :return:
    """
    with tarfile.open(out_file, 'w:gz') as f:
        for image in os.listdir(TEMP_FOLDER):
            path = os.path.join(TEMP_FOLDER, image)
            f.add(path, image) # Store with just the image name, ignore full path


def parse_args():
    """
    Parse arguments for the program.
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('in', type=str, default="manifest.txt", help='The manifest file to read from.')
    parser.add_argument('out', type=str, default="images.tar.gz", help='The output file to write to.')
    parser.add_argument('--processes', type=int, default=1, help='The number of processes to run.')

    return vars(parser.parse_args())


if __name__ == "__main__":
    args = parse_args()
    # Create the queue
    queue = JoinableQueue()

    # Start the consumers
    for x in range(args['processes']):
        consumer = Consumer(queue)
        consumer.start()

    mkdir(TEMP_FOLDER)

    build_jobs(args['in'], queue)

    # Add a poison pill to shut things down
    for x in range(args['processes']):
        queue.put(None)

    # Wait for the queue to terminate
    queue.join()

    # Compress all the images together
    compress_output(args['out'])


