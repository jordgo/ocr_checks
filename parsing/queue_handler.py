import base64
import json
import logging
import multiprocessing
import threading
import time
from json import JSONDecodeError
from multiprocessing import Pool
import queue
from multiprocessing.process import BaseProcess
from typing import List

import numpy as np

from main import process_img
from models.request_bcheck_data import RequestBankCheck
from utility.sending.by_url import send_result

_logger = logging.getLogger("app")


class QueueHandler:
    def __init__(self, pool: Pool, q: queue.Queue, pool_size: int):
        self.pool: multiprocessing.Pool = pool
        self.q = q
        self.pool_size = pool_size
        self.active_tasks_queue: queue.Queue = queue.Queue()
        self.event = threading.Event()
        _logger.info(f"QueueHandler started with pool_size: <{self.pool_size}>")

    @staticmethod
    def _process_request(data: RequestBankCheck):
        url = data.url
        img = data.img
        res = process_img(img)
        send_result(url, res)

    def start(self):
        work_queue = threading.Thread(target=self.modifyQueue)
        work_queue.start()

    def modifyQueue(self):
        _logger.info(f"modifyQueue started")
        while True:
            if self.event.isSet():
                break
            print('111111111111111111111 ', self.active_tasks_queue.qsize(), not self.q.empty())
            if self.active_tasks_queue.qsize() < self.pool_size and not self.q.empty():
                _logger.info(f"Checking queue")
                request_data = self.q.get()
                self.active_tasks_queue.put(1)
                self.pool.apply_async(self._process_request, [request_data], callback=self.process_finished)

            time.sleep(1)

    def process_finished(self, res):
        self.active_tasks_queue.get()
        print("============= Finished ============")

    def stop(self):
        self.event.set()
        _logger.info("QueueHandler stopped")


def create_errmsg(msg: str) -> dict:
    return {"error": msg}