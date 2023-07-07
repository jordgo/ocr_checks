import logging
import threading
import time

import requests


_logger = logging.getLogger("app")


def send_result(url: str, data: dict):
    res = None
    try:
        res = requests.post(url, data=data)
    except Exception as e:
        _logger.error(f"Failure to send response to url: <{url}>, error: <{e}>")

    if res is not None and res.status_code == 200:
        _logger.info(f"Sending successfully to url: <{url}>, data: <{data}>")
    else:
        _logger.error(f"Sending Failure, res={res}, url: <{url}>, data: <{data}>")


def send_result_parallel(url: str, data: dict):
    time.sleep(0.1)
    t = threading.Thread(target=send_result, kwargs={'url': url, 'data': data})
    t.start()