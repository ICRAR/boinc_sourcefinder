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
import unittest
import subprocess

INIT_FAIL_PATH = 'validator_tests/init/fail/'
INIT_SUCCEED_PATH = 'validator_tests/init/succeed/'
COMPARE_FAIL_PATH = 'validator_tests/compare/fail/'
COMPARE_SUCCEED_PATH = 'validator_tests/compare/succeed/'


def run_init(filename):
    return subprocess.call(['../server/duchamp/validator_duchamp_init.sh', filename])


def run_compare(filename1, filename2):
    return subprocess.call(['../server/duchamp/validator_duchamp_compare.sh', filename1, filename2])


class ValidatorTest(unittest.TestCase):

    def test_init_succeed(self):
        files = [os.path.join(INIT_SUCCEED_PATH, f) for f in os.listdir(INIT_SUCCEED_PATH)]

        for f in files:
            self.assertEqual(0, run_init(f), "File {0} succeeds".format(f))

    def test_init_fail(self):
        files = [os.path.join(INIT_FAIL_PATH, f) for f in os.listdir(INIT_FAIL_PATH)]

        for f in files:
            self.assertEqual(1, run_init(f), "File {0} fails".format(f))

    def test_compare_succeed(self):
        file1 = os.path.join(COMPARE_FAIL_PATH, "10_askap_cube_20_18_22_0")
        file2 = os.path.join(COMPARE_FAIL_PATH, "10_askap_cube_20_18_22_2")

        self.assertEqual(0, run_compare(file1, file2), "File {0} compared to file {1} succeeds".format(file1, file2))

    def test_compare_fail(self):
        file1 = os.path.join(COMPARE_FAIL_PATH, "10_askap_cube_20_18_22_0")
        file2 = os.path.join(COMPARE_FAIL_PATH, "10_askap_cube_20_18_22_1")
        file3 = os.path.join(COMPARE_FAIL_PATH, "10_askap_cube_20_18_22_2")

        self.assertEqual(1, run_compare(file1, file2), "File {0} compared to file {1} fails".format(file1, file2))
        self.assertEqual(1, run_compare(file2, file3), "File {0} compared to file {1} fails".format(file2, file3))


if __name__ == '__main__':
    unittest.main()