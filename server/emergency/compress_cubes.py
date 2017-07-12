#! /usr/bin/env python

from multiprocessing import JoinableQueue, Process, get_logger
from multiprocessing.util import SUBDEBUG
import logging
import gzip
import os

LOGGER = get_logger()


class Gzipper:
    def __init__(self, filename_in, filename_out):
        self.filename_in = filename_in
        self.filename_out = filename_out

    def __call__(self, *args, **kwargs):
        LOGGER.info('Compressing {0} to {1}'.format(self.filename_in, self.filename_out))

        with gzip.open(self.filename_out, 'wb') as write:
            with open(self.filename_in, 'r') as read:
                write.write(read.read())

        LOGGER.info('Done')


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

def is_number(char):
    return char in '0123456789'

def find_cube_set_number(name):

    numbers = ''
    first_number_idx = 0
    for i in range(0, len(name)):
        if is_number(name[i]):
            first_number_idx = i
            break

    while is_number(name[first_number_idx]):
        numbers += name[first_number_idx]
        first_number_idx += 1

    return int(numbers)

if __name__ == "__main__":
    formatter = logging.Formatter('[%(processName)s]:%(asctime)-15s:%(levelname)s:%(module)s:%(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.propagate = 0
    LOGGER.setLevel(SUBDEBUG)

    # Create the queue
    queue = JoinableQueue()

    # Start the consumers
    for x in range(8):
        consumer = Consumer(queue)
        consumer.start()

    base_folder = '/mnt/hidata/dingo/skynet/v1/skynet_cubelets'
    out_folder = '/scratch/sam/cubes'

    # Open the input file
    with open('/scratch/sam/files_to_get.txt', 'r') as f:
        for line in f:
            line = line[:-1]
            folder = os.path.join(base_folder, 'cubelets_{0}'.format(find_cube_set_number(line)))

            infile = os.path.join(folder, "{0}.fits".format(line))
            outfile = os.path.join(out_folder, "{0}.fits.gz".format(line))

            print "adding", infile, outfile

            queue.put(Gzipper(infile, outfile))

    # Add a poison pill to shut things down
    for x in range(8):
        queue.put(None)

    # Wait for the queue to terminate
    queue.join()
