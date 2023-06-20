import cv2
import numpy as np

from models.data_classes import RectangleData
from parsing.target_rectangles import _get_boxes_cnt
from utility.rectangle_utils.sentences import get_sentences


def cut_img(img: np.ndarray, config) -> np.ndarray:
    MAX_H_OF_WORD = config["env"]["MAX_H_OF_WORD"]
    MIN_H_OF_WORD = config["env"]["MIN_H_OF_WORD"]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 220, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    boxes_with_cnt: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours, MAX_H_OF_WORD, MIN_H_OF_WORD)
    rects = [r[0] for r in boxes_with_cnt]
    sentences = get_sentences(rects)
    frequency_dict = {}
    h, w, _ = np.shape(img)
    x_thresh = w * 0.3
    for sen in sentences:
        if sen.x < x_thresh:
            if len(frequency_dict) == 0:
                frequency_dict = {sen.x: 1}
            else:
                for dict_x in frequency_dict:
                    if dict_x - 2 < sen.x < dict_x + 2:
                        frequency_dict[dict_x] += 1
                        break
                else:
                    frequency_dict[sen.x] = 1

    x = max(frequency_dict, key=frequency_dict.get)

    img_cropped = img[0:h, x - 10:w]
    return img_cropped