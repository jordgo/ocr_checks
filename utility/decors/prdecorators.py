import logging
import time


_logger = logging.getLogger("app")


def print_time_of_script(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        diff = int(end - start)
        _logger.info("=============== Processing time: {}s ===============".format(diff))
        return res
    return wrapper
