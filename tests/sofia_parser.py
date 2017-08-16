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
from boinc_sourcefinder.server.sofia.output_parser import SofiaResult, save_csv

FAIL_PATH = 'sofia_parser_tests/parse_error/'
SUCCEED_PATH = 'sofia_parser_tests/succeed/'
NO_DATA_PATH = 'sofia_parser_tests/no_data/'

sofia_output_start = 'sofia_output_'
sofia_output_end = '_cat.xml'


class SofiaParserTest(unittest.TestCase):

    @staticmethod
    def get_parameter_number(filename):
        return int(filename[len(sofia_output_start):-len(sofia_output_end)])

    def test_succeed(self):
        files = os.listdir(SUCCEED_PATH)
        results = []

        for f in files:
            with open(os.path.join(SUCCEED_PATH, f), 'r') as open_file:
                result = SofiaResult(self.get_parameter_number(f), open_file.read())
                results.append(result)

                self.assertTrue(result.has_data, "has_data is true")
                self.assertIsNone(result.parse_error, "parse_error is None")
                self.assertTrue(len(result.data) > 0, "result.data length > 0")
                self.assertTrue(len(result.headings) > 0, "result.headings length > 0")
                self.assertTrue(len(result.types) > 0, "result.types length > 0")

        save_csv(results, "/tmp/succeed.csv")

        with open("/tmp/succeed.csv", 'r') as f:
            data = f.read()
            split = data.split(',')
            self.assertFalse(data == "No sources\n", "saved csv does not contain 'No sources'")
            self.assertTrue(len(split) > 2, "saved csv has data")

    def test_fail(self):
        files = os.listdir(FAIL_PATH)

        for f in files:
            with open(os.path.join(FAIL_PATH, f), 'r') as open_file:
                result = SofiaResult(self.get_parameter_number(f), open_file.read())

                self.assertFalse(result.has_data, "has_data is false")
                self.assertIsNotNone(result.parse_error, "parse_error is not None")
                self.assertTrue(len(result.data) == 0, "result.data length == 0")
                self.assertTrue(len(result.headings) == 0, "result.headings length == 0")
                self.assertTrue(len(result.types) == 0, "result.types length == 0")


if __name__ == '__main__':
    unittest.main()
