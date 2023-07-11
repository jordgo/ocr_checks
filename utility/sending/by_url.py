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
        period_sec = 60*2
        _logger.info(f"Next try in {int(period_sec/60)} minutes")
        time.sleep(period_sec)
        def sending(url, data):
            try:
                res = requests.post(url, data=data)
            except Exception as e:
                res = None
                _logger.error(f"Failure to send response to url: <{url}>, error: <{e}>")

            if res is not None and res.status_code == 200:
                _logger.info(f"Sending successfully to url: <{url}>, data: <{data}>")
            else:
                _logger.error(f"Sending Failure, res={res}, url: <{url}>, data: <{data}>")

        t = threading.Thread(target=sending, kwargs={'url': url, 'data': data})
        t.start()

    if res is not None and res.status_code == 200:
        _logger.info(f"Sending successfully to url: <{url}>, data: <{data}>")
    else:
        _logger.error(f"Sending Failure, res={res}, url: <{url}>, data: <{data}>")


def send_result_parallel(url: str, data: dict):
    time.sleep(0.1)
    t = threading.Thread(target=send_result, kwargs={'url': url, 'data': data})
    t.start()