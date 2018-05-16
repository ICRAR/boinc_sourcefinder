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
1. Form a list of all items in s3 to download, including the size of each item.

loop:
2.  Pick a set of items from the list to download and pull them down into a folder.
3.  Erase those items from the list and re-save it
4.  Wait 24 hours, continue until all items are downloaded
"""

# Note: this script is designed to be stand alone, and will only import from external libraries.
from botocore.client import Config
import boto3
import pickle
import argparse
import logging
import os
import errno

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)
LOG = logging.getLogger(__name__)


class S3Helper:
    def __init__(self, bucket_name):
        self.s3 = boto3.resource('s3', config=Config(connect_timeout=99999, read_timeout=99999))
        self.bucket = self.s3.Bucket(bucket_name)

    def get_object_list(self):
        s3_objects = []
        ignored = 0
        itr = iter(self.bucket.objects.all())
        index = 0
        while True:
            try:
                s3_object = next(itr)
                key = s3_object.key
                if key.endswith(".md5") or key.endswith(".err") or key.endswith(".out"):
                    ignored += 1
                    continue
                s3_objects.append(s3_object.key)
                if index % 100 == 0:
                    LOG.info("Objects Collected: {0}, Ignored: {1}".format(index, ignored))
                index += 1
            except StopIteration:
                break  # finished iterating
            except Exception as e:
                LOG.exception(e)
                continue  # try again forever

        return s3_objects

    def download_file(self, key, path):
        self.bucket.download_file(key, path)


def command_get_objects(args):
    s3 = S3Helper('icrar.sourcefinder.files')
    s3_objects = s3.get_object_list()
    with open(args.file, 'w') as f:
        pickle.dump(s3_objects, f, pickle.HIGHEST_PROTOCOL)


def command_download_objects(args):
    s3 = S3Helper('icrar.sourcefinder.files')
    # If the in progress file exists, use that one.
    in_progress_file = args.file + "_inprogress"
    objects_file = in_progress_file if os.path.exists(in_progress_file) else args.file

    with open(objects_file, 'r') as f:
        s3_objects = pickle.load(f)

    try:
        i = 0
        while True:
            try:
                s3_object = s3_objects.pop()
            except IndexError:
                # Gone through all items
                break

            # Create the local directory structure for the item
            directory = os.path.join(args.path, os.path.dirname(s3_object))
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

            # Download the item
            LOG.info("Downloading: {0}. {1} remaining".format(s3_object, len(s3_objects)))
            s3.download_file(s3_object, os.path.join(directory, os.path.basename(s3_object)))

            if i % 100 == 0:
                LOG.info("Saving progress. {0} remaining".format(len(s3_objects)))
                with open(in_progress_file, 'w') as f:
                    pickle.dump(s3_objects, f, pickle.HIGHEST_PROTOCOL)
            i += 1
    except:
        with open(in_progress_file, 'w') as f:
            pickle.dump(s3_objects, f, pickle.HIGHEST_PROTOCOL)


def parse_args():
    parser = argparse.ArgumentParser()
    common_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    get_objects_parser = subparsers.add_parser('get_objects', parents=[common_parser], help='Get a list of all applicable items in the s3 bucket.')
    get_objects_parser.add_argument('--file', help="The filename to save the items to.")
    get_objects_parser.set_defaults(func=command_get_objects)

    download_objects_parser = subparsers.add_parser('download_objects', parents=[common_parser], help='Download part of the objects in the s3 bucket.')
    download_objects_parser.add_argument('--file', help="The filename containing the objects to download.")
    download_objects_parser.add_argument('--path', help="The path to download the files to.")
    download_objects_parser.set_defaults(func=command_download_objects)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.func(args)
