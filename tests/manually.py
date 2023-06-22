import cv2
import numpy as np

from definition import ROOT_DIR
from parsing.target_rectangles import get_rect_by_contours
from utility.rectangle_utils.prepare_img import cut_img
from utility.rectangle_utils.sentences import get_sentences


def test_get_rect_by_contours_manually(config):
    img = cv2.imread(ROOT_DIR + "/tests/imgs/vtb_1.jpeg")

    img_c = np.copy(img)
    img_cropped = cut_img(img, config)
    rectangles = get_rect_by_contours(img_cropped, config)
    sentences = rectangles #get_sentences(rectangles)
    for r in sentences:
        cv2.rectangle(img_cropped, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 2)

    cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 1700, 900)
    cv2.imshow("Test", img_cropped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    assert True