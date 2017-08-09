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
Parses SoFiA output files
"""

import sys


class SofiaResult:
    def __init__(self, data):
        self.raw_data = data
        self.token_gen = self._get_token(self.raw_data)
        self.token = None

        self.headings = []
        self.types = []
        self.data = []

        self.parse_error = None
        self.has_data = False

        self._parse()

    @staticmethod
    def _get_token(data):
        curr_token = ""
        for char in data:

            if char == ' ':
                if len(curr_token) > 0:
                    yield curr_token
                    curr_token = ""
            elif char == '\n':
                if len(curr_token) > 0:
                    yield curr_token
                curr_token = ""
                yield '\n'  # Ensure we yield the \n char!
            else:
                curr_token += char

        if len(curr_token) > 0:
            yield curr_token
        yield None

    @staticmethod
    def _is_number(token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_int(token):
        try:
            int(token)
            return True
        except ValueError:
            return False

    def _next_token(self):
        self.token = next(self.token_gen)

    def _check_no_results(self):
        return self.token.startswith('!!!')

    def _parse_comment(self):
        if self.token.startswith('#'):
            while self.token is not None and not self.token.endswith('\n'):
                self._next_token()

            if self.token.endswith('\n'):
                self._next_token()  # Step over the new line

    def _parse_line(self, array):
        if self.token == "#":
            self._next_token()  # Skip the # at the start

        while self.token is not None and not self.token.endswith('\n'):
            array.append(self.token)
            self._next_token()

        if self.token.endswith('\n'):
            self._next_token()  # Step over the new line

    def _parse_data(self):
        line = []
        heading_index = 0

        while self.token is not None and not self.token.endswith('\n'):

            if self.headings[heading_index] == "name":
                # Need to parse multiple tokens for the name.
                combined_token = self.token

                self._next_token()
                while not self._is_number(self.token):
                    combined_token += ' {0}'.format(self.token)
                    self._next_token()

                line.append(combined_token)

            if self._is_int(self.token):
                line.append(int(self.token))
            else:
                line.append(float(self.token))

            self._next_token()
            heading_index += 1

        # Step over the \n
        if self.token is not None and self.token.endswith('\n'):
            self._next_token()

        if len(line) > 0:
            self.data.append(line)
            return True
        else:
            return False

    def _parse(self):
        try:
            self._next_token()

            if self._check_no_results():
                return

            self._parse_comment()  # Skip the first line
            self._parse_line(self.headings)  # Parse out the header
            self._parse_line(self.types)  # Parse the data types
            self._parse_comment()  # Skip the data indexes

            while self._parse_data():
                pass

            self.has_data = True
        except Exception as e:
            self.parse_error = e.message
            return

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:

        result = SofiaResult(f.read())

        if result.parse_error:
            print "Parse error: {0}".format(result.parse_error)
        elif result.has_data:
            print result.headings
            print result.types

            for data in result.data:
                print data
        else:
            print "No data"
