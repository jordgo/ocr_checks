# import logging
#
# import numpy as np
# import yaml
#
# from definition import ROOT_DIR
# from models.data_classes import RectangleData
# from parsing.by_contours import get_img_text_by_contours
# from parsing.target_rectangles import get_rect_by_contours
# from utility.rectangle_utils.prepare_img import cut_img_by_rect
#
# _logger = logging.getLogger("app")
#
#
# with open(ROOT_DIR + "/conf/config.yml", 'r') as file:
#     config = yaml.safe_load(file)
#
#
# def process_rectangle_img(img: np.ndarray, rect: RectangleData) -> str:
#     cropped = cut_img_by_rect(img, rect)
#     rects = get_rect_by_contours(cropped, config)
#     rects_with_text = get_img_text_by_contours(cropped, rects)
#     sorted_by_x = sorted(rects_with_text, key=lambda r: r.x)
#     _logger.info(sorted_by_x)
#     return ' '.join([r.text for  r in sorted_by_x])