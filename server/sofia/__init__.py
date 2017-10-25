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

PARAMETERS = [
    "id",
    "name",
    "x",
    "y",
    "z",
    "x_geo",
    "y_geo",
    "z_geo",
    "rms",
    "rel",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "n_pix",
    "n_los",
    "n_chan",
    "ra",
    "dec",
    "lon",
    "lat",
    "freq",
    "velo",
    "w20",
    "w50",
    # "wm50",
    "f_peak",
    "f_int",
    # "f_wm50",
    "ell_maj",
    "ell_min",
    "ell_pa",
    "ell3s_maj",
    "ell3s_min",
    "ell3s_pa",
    "kin_pa",
    "bf_a",
    "bf_b1",
    "bf_b2",
    "bf_c",
    "bf_xe",
    "bf_xp",
    "bf_w",
    "bf_chi2",
    "bf_flag",
    "bf_z",
    "bf_w20",
    "bf_w50",
    "bf_f_peak",
    "bf_f_int"
]

PARAMETERS_STRING = ""
for idx, parameter in enumerate(PARAMETERS):
    PARAMETERS_STRING += "'{0}'".format(parameter)
    if idx < len(PARAMETERS) - 1:
        PARAMETERS_STRING += ", "
