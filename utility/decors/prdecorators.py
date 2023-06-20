import time


def print_time_of_script(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        diff = int(end - start)
        print("Processing time is {}s".format(diff))
        return res
    return wrapper
