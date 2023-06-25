import logging

import cv2
import numpy as np
import yaml

from definition import ROOT_DIR
from models.data_classes import RectangleData
from parsing.by_contours import get_img_text_by_contours, _get_results_by_tesseract_configs, _get_text_by_max_conf
from parsing.target_rectangles import get_rect_by_contours
from utility.rectangle_utils.prepare_img import cut_img_by_rect

_logger = logging.getLogger("app")


def process_rectangle_img(img: np.ndarray, rect: RectangleData) -> str:
    cropped = cut_img_by_rect(img, rect)
    results, _ = _get_results_by_tesseract_configs(cropped)
    text, conf, r_coef, frame, _ = _get_text_by_max_conf(results) if results else ("", 0, 0, np.ndarray([]))
    _logger.info(text)

    # cv2.imshow("Test", cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return text #' '.join([r.text for  r in sorted_by_x])