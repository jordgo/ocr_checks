import base64
import io
import logging
import multiprocessing
import queue

import numpy as np
from flask import Flask, request
from pydantic import ValidationError

from models.request_bcheck_data import RequestBankCheck
from parsing.queue_handler import QueueHandler

from waitress import serve
import imageio

_logger = logging.getLogger("app")
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

app = Flask(__name__)
q = queue.Queue(1000)


def create_response(status: str, error: str) -> dict:
    return {"status": status, "error": error}


@app.route('/', methods=['POST'])
def bank_check():
    data_dict = request.get_json()
    _logger.info(f"Received data: <{data_dict}>")
    try:
        url: str = data_dict['url']
        img_base_64 = data_dict['img'].split(",")[1]
        img = np.array(imageio.v3.imread(io.BytesIO(base64.b64decode(img_base_64))))
        data = RequestBankCheck(url, img)
        q.put(data, block=True, timeout=60)
        _logger.info(f"Data added for url: <{url}>")
    except queue.Full as e:
        _logger.error(f"Queue is Full")
        return create_response("error", "Queue is Full")
    except ValidationError as e:
        _logger.error(f"ValidationError, <{e.errors()}>")
        return create_response("error", f"ValidationError, <{e.errors()}>")
    except Exception as e:
        _logger.error(f"Wrong parameters, <{e}>")
        return create_response("error", f"Wrong parameters, <{e}>")

    return create_response("ok", "")


if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 9000

    pool_size = 4 #int(multiprocessing.cpu_count() / 2)
    pool = multiprocessing.Pool(pool_size, maxtasksperchild=100)
    handler = QueueHandler(pool, q, pool_size)
    handler.start()

    # app.run(host=HOST, port=PORT)
    serve(app, host=HOST, port=PORT)
    pool.close()
    pool.join()
    handler.stop()
    _logger.info(f"Server shutdown")

