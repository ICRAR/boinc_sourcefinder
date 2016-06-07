import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

import boto3


def get_file_upload_key(workunit_name, file_name):
    return '{0}/{1}'.format(workunit_name, file_name)


class S3Helper:

    def __init__(self, bucket_name):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)

    def file_upload(self, local_file, remote_key):
        close = False
        if isinstance(local_file, basestring):
            close = True
            local_file = open(local_file, 'r')

        self.bucket.put_object(Key=remote_key, Body=local_file)

        if close:
            local_file.close()