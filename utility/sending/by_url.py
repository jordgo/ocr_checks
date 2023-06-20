import logging

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