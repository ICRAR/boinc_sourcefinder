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
import xml.etree.ElementTree as ET


def save_csv(results, filename):
    # First, confirm the headers are all the same
    with_results = [result for result in results if result.has_data]

    with open(filename, 'w') as f:
        if len(with_results) == 0:
            # No data at all
            f.write("No sources\n")
        else:
            # Write out data
            # Confirm all headings are the same
            first_result = with_results[0]
            for result in with_results[1:]:
                if result.headings != first_result.headings:
                    raise Exception("Headings don't match for all results")
                if result.types != first_result.types:
                    raise Exception("Types don't match for all results")

            f.write('parameter_number,{0}\n'.format(','.join(first_result.headings)))
            f.write('int,{0}\n'.format(','.join(first_result.types)))

            for result in results:
                for line in result.data:
                    f.write('{0},{1}\n'.format(result.parameter_number, ','.join(line)))


class SofiaResult:
    def __init__(self, parameter_number, data):
        self.parameter_number = parameter_number
        self.raw_data = data
        self.has_data = False
        self.parse_error = None

        self.headings = []
        self.types = []
        self.data = []

        self._parse()

    def _parse_xml(self):
        root = ET.fromstring(self.raw_data)
        self._parse_xml_headings(root)
        self._parse_xml_data(root)

    def _parse_xml_headings(self, root):
        table = root.find("RESOURCE").find("TABLE")
        fields = table.findall("FIELD")

        for field in fields:
            name = field.get("name")
            type = field.get("datatype")

            self.headings.append(name)
            self.types.append(type)

    def _parse_xml_data(self, root):
        table = root.find("RESOURCE").find("TABLE").find("DATA").find("TABLEDATA")
        fields = table.findall("TR")

        for field in fields:
            entry = []
            elements = field.findall("TD")
            for element in elements:
                entry.append(element.text)
            self.data.append(entry)

    def _parse(self):
        try:
            self._parse_xml()

            self.has_data = True
        except Exception as e:
            self.parse_error = e.message
            return

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:

        result = SofiaResult(0, f.read())

        if result.parse_error:
            print "Parse error: {0}".format(result.parse_error)
        elif result.has_data:
            print result.headings
            print result.types

            for data in result.data:
                print data

            save_csv([result], "saved.csv")
        else:
            print "No data"
