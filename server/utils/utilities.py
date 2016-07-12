# A generic utilities package containing misc functions and classes used by server apps.


def retry_on_exception(function, exception, num_retries):

    while num_retries > 0:
        try:
            function()
            num_retries = 0
        except exception:
            num_retries -= 1
