import cv2
import numpy as np

from definition import ROOT_DIR
from parsing.target_rectangles import get_rect_by_contours
from utility.rectangle_utils.prepare_img import cut_img
from utility.rectangle_utils.sentences import get_sentences


def test_get_rect_by_contours_manually(config):
    # img = cv2.imread("../../imgs/image.png")
    # img = cv2.imread("../../imgs/html_space_issue.png")
    # img = cv2.imread(ROOT_DIR + "/tests/imgs/second_00:13:18.020000.png")
    # img = cv2.imread(ROOT_DIR + "/tests/imgs/missed_pro_operaive_alingment.png")
    # img = cv2.imread(ROOT_DIR + "/tests/imgs/extra_rect_issue.png")
    img = cv2.imread(ROOT_DIR + "/tests/imgs/tinkof_2.jpeg")

    img_c = np.copy(img)
    img_cropped = cut_img(img, config)
    rectangles = get_rect_by_contours(img_cropped, config)
    sentences = get_sentences(rectangles)
    for r in sentences:
        cv2.rectangle(img_cropped, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 2)


    # all_rectangles = get_rect_by_contours(img_c, config, is_debug=True)
    # for r_p in all_rectangles:
    #     r, (count_of_points_per_area, count_boxes) = r_p
    #     count_text = str(count_of_points_per_area) + "-" + str(count_boxes)
    #     cv2.putText(img, count_text, (r.x-10, r.y-10),
    #                 fontFace=cv2.FONT_HERSHEY_COMPLEX,
    #                 fontScale=0.3,
    #                 color=(0, 255, 0),
    #                 thickness=1,
    #                 lineType=cv2.LINE_AA,
    #                 )
    #
    # page_template = BODY_WITH_LEFT_PAYLOAD
    # h, w, _ = img.shape
    # print(h,w)
    # header = page_template["header"]
    # cv2.line(img, (0, header), (w, header), (255, 0, 0), 2)
    # footer = page_template["footer"]
    # cv2.line(img, (0, h - footer), (w, h - footer), (255, 0, 0), 2)
    # right_border = page_template["right_border"]
    # cv2.line(img, (right_border, 0), (right_border, h), (255, 0, 0), 2)
    # left_border = page_template["left_border"]
    # cv2.line(img, (w - left_border, 0), (w - left_border, h), (255, 0, 0), 2)
    # body_left = page_template["body"]["left_side"]
    # cv2.line(img, (body_left, 0), (body_left, h), (255, 0, 0), 2)

    cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 1700, 900)
    cv2.imshow("Test", img_cropped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    assert True