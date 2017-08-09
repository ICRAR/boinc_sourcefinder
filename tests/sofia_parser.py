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
from boinc_sourcefinder.server.sofia.output_parser import SofiaResult

FAIL_PATH = 'sofia_parser_tests/parse_error/'
SUCCEED_PATH = 'sofia_parser_tests/succeed/'
NO_DATA_PATH = 'sofia_parser_tests/no_data/'


class SofiaParserTest(unittest.TestCase):

    def test_succeed(self):
        files = [os.path.join(SUCCEED_PATH, f) for f in os.listdir(SUCCEED_PATH)]

        for f in files:
            with open(f, 'r') as open_file:
                result = SofiaResult(open_file.read())

                self.assertTrue(result.has_data, "has_data is true")
                self.assertIsNone(result.parse_error, "parse_error is None")
                self.assertTrue(len(result.data) > 0, "result.data length > 0")
                self.assertTrue(len(result.headings) > 0, "result.headings length > 0")
                self.assertTrue(len(result.types) > 0, "result.types length > 0")

    def test_fail(self):
        files = [os.path.join(FAIL_PATH, f) for f in os.listdir(FAIL_PATH)]

        for f in files:
            with open(f, 'r') as open_file:
                result = SofiaResult(open_file.read())

                self.assertFalse(result.has_data, "has_data is false")
                self.assertIsNotNone(result.parse_error, "parse_error is not None")
                self.assertTrue(len(result.data) == 0, "result.data length == 0")
                self.assertTrue(len(result.headings) == 0, "result.headings length == 0")
                self.assertTrue(len(result.types) == 0, "result.types length == 0")

    def test_no_data(self):
        files = [os.path.join(NO_DATA_PATH, f) for f in os.listdir(NO_DATA_PATH)]

        for f in files:
            with open(f, 'r') as open_file:
                result = SofiaResult(open_file.read())

                self.assertFalse(result.has_data, "has_data is false")
                self.assertIsNone(result.parse_error, "parse_error is None")
                self.assertTrue(len(result.data) == 0, "result.data length == 0")
                self.assertTrue(len(result.headings) == 0, "result.headings length == 0")
                self.assertTrue(len(result.types) == 0, "result.types length == 0")

if __name__ == '__main__':
    unittest.main()
