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
import csv


class CSVCompare:

    def __init__(self, csv_data):
        self.threshold = 0.0001

        self.reason = None  # Reason why the last compare failed
        self.unmatching_row = None  # The row that didn't match

        # Load the CSV rows.
        csv_reader = csv.DictReader(csv_data)
        self.rows = [r for r in csv_reader]
        self.cell_count = sum([len(c) for c in self.rows])

    @staticmethod
    def _to_float(cell):
        try:
            return float(cell)
        except ValueError:
            return None

    def _compare_cells(self, row1, row2):
        for cell1, cell2 in zip(row1, row2):
            float1 = self._to_float(cell1)
            float2 = self._to_float(cell2)

            if float1 is None and float2 is None:
                continue  # Skip comparing these
            elif float1 is None or float2 is None:
                return False
            elif abs(float1 - float2) > self.threshold:
                return False
        return True

    def compare(self, other):
        self.unmatching_row = None
        # Search for a matching rows. All of my rows must match with one of their rows.
        for my_row in self.rows:
            found = False
            for other_row in other.rows:
                if self._compare_cells(my_row.values(), other_row.values()):
                    found = True
                    break

            if not found:
                self.unmatching_row = my_row
                return False

        return True

    def __eq__(self, other):
        """

        :param other:
        :type other: CSVCompare
        :return:
        """
        self.reason = None
        try:
            if type(other) != type(self):
                self.reason = "Other object is incorrect type"
            elif len(self.rows) != len(other.rows):
                self.reason = "Length of rows differs: {0} to {1}".format(len(self.rows), len(other.rows))
            elif self.cell_count != other.cell_count:
                self.reason = "Length of cells differs: {0}, to {1}".format(self.cell_count, other.cell_count)
            elif not self.compare(other):
                self.reason = "Row doesn't have matching row in other: \n {0}".format(self.unmatching_row)

        except Exception as e:
            self.reason = "Exception: {0}".format(e.message)

        return self.reason is None