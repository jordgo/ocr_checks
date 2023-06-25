from typing import List

import cv2
import numpy as np

from models.data_classes import RectangleData
from utility.rectangle_utils.sentences import get_sentences, get_sentences2


# THRESHOLD_CONTOURS_POINTS = 1000


def _get_rect_lines(gray: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (7, 7), 0.5)
    # ret, thresh = cv2.threshold(blur, 50, 150, 0
    edge = cv2.Canny(blur, 0, 50, 3)

    contours, hierarchy = cv2.findContours(edge, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    mask = np.copy(gray) * 0

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 70:
                cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), 5)
    return mask


def _get_lines(gray: np.ndarray) -> np.ndarray:
    """getting the lines of a drawing for later deletion"""
    blur_gray = cv2.GaussianBlur(gray, (7, 7), 0)
    # # io.imagesc(blur_gray)
    # edges = cv2.Canny((blur_gray * 255).astype(np.uint8), 10, 200, apertureSize=5)
    # rho = 1  # distance resolution in pixels of the Hough grid
    # theta = np.pi / 180  # angular resolution in radians of the Hough grid
    # threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    # min_line_length = 70  # minimum number of pixels making up a line
    # max_line_gap = 3  # maximum gap in pixels between connectable line segments
    line_image = np.copy(gray) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    # lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
    #                         min_line_length, max_line_gap)
    #
    # lines = lines if (lines is not None) and lines.size != 0 else []
    # for line in lines:
    #     for x1, y1, x2, y2 in line:
    #         cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 5)

    line_detector: cv2.LineSegmentDetector = cv2.createLineSegmentDetector()
    lines = line_detector.detect(blur_gray)[0]

    for j in range(lines.shape[0]):
        x1, y1, x2, y2 = lines[j, 0, :]
        if np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2])) > 100:
            cv2.line(line_image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 5)

    return line_image


def _is_black_bg(gray: np.ndarray) -> bool:
    """
    define dark or light background
    :param gray: np.ndarray
    :return: bool - True if is black
    """
    h, w = gray.shape
    cropped = gray[0:int(h * 0.1), 0:int(w * 0.1)]
    f_gray = cropped.flatten()
    c_count = {"0": 0, "255": 0}
    for i in range(len(f_gray)):
        if f_gray[i] > 127:
            c_count["255"] += 1
        else:
            c_count["0"] += 1
    return c_count["0"] > c_count["255"]


def _get_boxes_cnt(contours: [[int, int]],
                   max_h: int,
                   min_h: int,
                   ) -> [(RectangleData, [[int, int]])]:
    rect_with_cnt = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if min_h < h < max_h:
            r = RectangleData(x=x, y=y, w=w, h=h, text='')
            rect_with_cnt.append((r, cnt))
    return rect_with_cnt


def _get_count_of_points_per_area(outer_rect: RectangleData,
                                  inner_rect_cnt: [(RectangleData, [[int, int]])]
                                  ) -> (int, int):
    """
    determines the len of contour per area of the word
    :param outer_rect: RectangleData - outer rectangle containing the whole word
    :param inner_rect_cnt: [(RectangleData, [[int, int]])] - inner rectangles with letters
    :return: (int, int) - number of contour points per unit area of the outer rectangle - number of inner-boxes DEBUGONLY
    """
    x, y, w, h, _ = outer_rect

    inner_cnt_sizes = []
    prev_rect: RectangleData = None
    for rect, cnt in inner_rect_cnt:
        if rect in outer_rect:
            if True: #prev_rect is None or rect.x - prev_rect.x - prev_rect.w < 10:
                prev_rect = rect
                ix, iy, iw, ih, _ = rect
                len_contour_per_area = cv2.arcLength(cnt, closed=False) / (iw * ih)
                inner_cnt_sizes.append(len_contour_per_area)

    count_of_points_per_area = sum(inner_cnt_sizes) #/ (w * h)
    return int(count_of_points_per_area * 1000), len(inner_cnt_sizes)


def get_rect_by_contours(orig_img: np.ndarray, config, is_debug: bool = False) -> List[RectangleData]:
    """
    getting rectangles containing text contours
    :param orig_img: original image
    :param config: list
    :param is_debug: bool - DEBUG ONLY
    :return:list[RectangleData] - without text
    """
    MAX_H_OF_WORD = config["env"]["MAX_H_OF_WORD"]
    MIN_H_OF_WORD = config["env"]["MIN_H_OF_WORD"]
    # MORPH_KERNEL_SIZE = 5
    # morph_kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE))

    gray = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
    is_black_bg = False #_is_black_bg(gray)
    bg_color = [0, 0, 0] if is_black_bg else [255, 255, 255]

    rect_mask_img = _get_rect_lines(gray)
    np.place(gray, rect_mask_img, bg_color)
    # lines_img = _get_lines(gray)
    # np.place(gray, lines_img, bg_color)

    thresh_binary_param = cv2.THRESH_BINARY #if is_black_bg else cv2.THRESH_BINARY_INV
    # ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | thresh_binary_param)
    ret, thresh = cv2.threshold(gray, 220, 255, thresh_binary_param)

    # dilate_img = cv2.dilate(thresh, kernel=morph_kernel, iterations=1)

    contours_origin, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # contours_with_dilate, _ = cv2.findContours(dilate_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    orig_boxes_with_cnt: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours_origin,
                                                                          MAX_H_OF_WORD,
                                                                          MIN_H_OF_WORD)
    # boxes_with_cnt: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours_with_dilate,
    #                                                                  MAX_H_OF_WORD,
    #                                                                  MIN_H_OF_WORD)

    rect_possibly_contains_text = get_sentences2([o[0] for o in orig_boxes_with_cnt]) # []
    # for bc in boxes_with_cnt:
    #     box, cnt = bc
    #     count_of_points_per_area, count_boxes = _get_count_of_points_per_area(box, orig_boxes_with_cnt)
    #     if count_of_points_per_area < 300 or box.h > MAX_H_OF_WORD or box.h < MIN_H_OF_WORD:
    #         continue
    #     if is_debug:
    #         rect_possibly_contains_text.append((box, (count_of_points_per_area, count_boxes)))  # DEBUG ONLY
    #     else:
    #         rect_possibly_contains_text.append(box)

    # for r, cnt in orig_boxes_with_cnt:
    #     cv2.rectangle(orig_img, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 1)
    # for r, cnt in orig_boxes_with_cnt_external:
    #     cv2.rectangle(orig_img, (r.x, r.y), (r.x + r.w, r.y + r.h), (255, 0, 0), 1)
    # for r, cnt in boxes_with_cnt:
    #     cv2.rectangle(orig_img, (r.x, r.y), (r.x + r.w, r.y + r.h), (255, 0, 0), 2)
    #
    # cv2.drawContours(orig_img, contours_with_dilate[-2:-1], -1, (255, 0, 0), 3)
    #
    # cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Test", 1700, 900)
    # cv2.imshow("Test", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return rect_possibly_contains_text
