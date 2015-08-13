#
#    (c) UWA, The University of Western Australia
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA, 2012-2013
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
Setup the wrappers around the BOINC 'C' libraries
"""

from distutils.core import setup
from distutils.extension import Extension
import os
from Cython.Build import cythonize

PY_BOINC = "py_boinc"
SOURCES = ['py_boinc.pyx','c_project/create_work.cpp']

if os.path.exists('/home/ec2-user'):
    INCLUDE_DIRS = ['/home/ec2-user/storage/boinc/sched',
                    '/home/ec2-user/storage/boinc/api',
                    '/home/ec2-user/storage/boinc/lib',
                    '/home/ec2-user/storage/boinc/db',
                    '/home/ec2-user/storage/boinc/tools',
                    '/home/ec2-user/storage/boinc',
                    '/usr/include/mysql']
    LIBRARY_DIRS = ['/usr/lib64/mysql/']
    extensions = [Extension(PY_BOINC,
                            sources=SOURCES,
                            include_dirs=INCLUDE_DIRS,
                            library_dirs=LIBRARY_DIRS,
                            extra_objects=['/home/ec2-user/storage/boinc/sched/libsched.a',
                                           '/home/ec2-user/storage/boinc/lib/libboinc.a',
                                           '/home/ec2-user/storage/boinc/lib/libboinc_crypt.a',
                                           '/home/ec2-user/storage/boinc/api/libboinc_api.a'],
                            libraries=['mysqlclient', 'ssl', 'crypto'],
                            )]
else:
    INCLUDE_DIRS = ['/Users/21298244/Documents/boinc-master/',
                    '/Users/21298244/Documents/boinc-master/db',
                    '/Users/21298244/Documents/boinc-master/sched',
                    '/Users/21298244/Documents/boinc-master/lib',
                    '/Users/21298244/Documents/boinc-master//clientgui/mac',
                    '/Users/21298244/Documents/boinc-master/tools',
                    '/usr/local/mysql-5.6.25-osx10.8-x86_64/include',]
    LIBRARY_DIRS = ['/usr/local/mysql-5.6.25-osx10.8-x86_64/lib']

    extensions = [Extension('create_work',
                            sources=SOURCES,
                            include_dirs=INCLUDE_DIRS,
                            library_dirs=LIBRARY_DIRS,
                            libraries=['boinc', 'boinc_api', 'mysqlclient', 'ssl', 'crypto'],
                            )]
setup(
    name=PY_BOINC,
    version='1.0',
    ext_modules=cythonize(
        extensions,
        name=PY_BOINC,
        language="c")
)
