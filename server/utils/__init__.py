# A generic utilities package containing misc functions and classes used by server apps.
import os, errno, tarfile, importlib


class DirStack:
    """
    DirStack is a simple helper class that allows the user to push directories on to the stack then
    pop them off later. If you want to change the working directory of the program, use stack.push() then
    os.chdir(dir).
    Later, to restore the previous directory, use stack.pop()
    """

    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append(os.getcwd())

    def pop(self):
        os.chdir(self.stack.pop())


def retry_on_exception(function, exception, num_retries):

    while num_retries > 0:
        try:
            return function()
        except exception:
            num_retries -= 1


def make_path(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def extract_tar(tar, path):
    with tarfile.open(tar) as tf:
        make_path(path)
        tf.extractall(path)


def module_import(module_name, app_name):
    import_path = app_name + '.' + module_name
    return importlib.import_module(import_path)