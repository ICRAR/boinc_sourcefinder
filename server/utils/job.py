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
Job processing module.
"""

import logging

from multiprocessing.util import SUBDEBUG
from multiprocessing import Process, get_logger
from multiprocessing.queues import JoinableQueue

LOGGER = get_logger()
formatter = logging.Formatter('[%(processName)s]:%(asctime)-15s:%(levelname)s:%(module)s:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
LOGGER.propagate = 0
LOGGER.setLevel(SUBDEBUG)


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
            # LOGGER.info('Getting a task')
            next_task = self._queue.get()
            if next_task is None:
                # Poison pill means shutdown this consumer
                LOGGER.info('Exiting consumer')
                self._queue.task_done()
                return
            # LOGGER.info('Executing the task')
            # noinspection PyBroadException
            try:
                next_task()
            except:
                LOGGER.exception('Exception in consumer')
            finally:
                self._queue.task_done()


class JobQueue(JoinableQueue):
    def __init__(self, num_consumers):
        """
        Creates a job queue with a set number of job processes.
        :param num_consumers: Number of job processes to use.
        :return:
        """
        JoinableQueue.__init__(self, maxsize=0)
        self.consumers = [Consumer(self) for _ in range(num_consumers)]
        self.started = False

    def start(self):
        """
        Starts all of the consumer threads.
        :return:
        """
        if not self.started:
            for consumer in self.consumers:
                consumer.start()

            self.started = True

    def join(self):
        """
        Waits for all of the consumer threads to complete
        :return:
        """
        for _ in self.consumers:
            self.put(None)

        self.start()  # Ensure running
        JoinableQueue.join(self)
