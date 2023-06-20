import base64
import json
import logging.config
import subprocess
from json import JSONDecodeError

import click as click
import cv2
import numpy as np
import yaml
from pytesseract import pytesseract

from conf.logging_conf import LOGGING_CONFIG
from definition import ROOT_DIR
from models.type_selector import find_type
from parsing.by_contours import get_img_text_by_contours
from parsing.target_rectangles import get_rect_by_contours
from utility.rectangle_utils.prepare_img import cut_img
from utility.rectangle_utils.sentences import get_sentences

logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")

with open(ROOT_DIR + "/conf/config.yml", 'r') as file:
    config = yaml.safe_load(file)


tesseract_path = subprocess.run(['which', 'tesseract'], stdout=subprocess.PIPE) \
    .stdout.decode('utf-8').replace('\n', '')
pytesseract.tesseract_cmd = tesseract_path


# @click.command()
# @click.argument('file_path', type=click.Path(exists=True))
def main(file_path: str) -> dict:
    # file_path: str = ROOT_DIR + "/tests/imgs/sber_1.jpeg"
    img = cv2.imread(file_path)
    res = process_img(img)
    return res


def process_img(img: np.ndarray) -> dict:
    img_cropped = cut_img(img, config)
    rects = get_rect_by_contours(img_cropped, config)
    sentences = get_sentences(rects)
    rects_with_text = get_img_text_by_contours(img_cropped, sentences)
    sorted_by_y = sorted(rects_with_text, key=lambda r: r.y)
    check_type = find_type(sorted_by_y)
    print([r.text for r in sorted_by_y])
    print(check_type.to_dict)
    return check_type.to_dict


if __name__ == "__main__":
    main(ROOT_DIR + "/tests/imgs/sber_1.jpeg")
