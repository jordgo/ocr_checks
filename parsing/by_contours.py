import logging
import subprocess
import time
from typing import List, Tuple

import cv2
import easyocr
import numpy as np
from pytesseract import pytesseract

from definition import ROOT_DIR
from parsing.post_process import fix_word
from utility.decors.prdecorators import print_time_of_script
from models.data_classes import TesseractResp, RectangleData
from utility.saving.save_to_dir import saving

_logger = logging.getLogger("app")

EASY_OCR_CONF = 0.8
TESSERACT_QUALITY = 89
TESSERACT_QUALITY_MIN =70  # 70
TESSERACT_DIGITS_QUALITY = 95
TESSERACT_DIGITS_QUALITY_MIN = 91

TESSERACT_BLACKLIST = '©@'

TESSERACT_CONF_DEFAULT = f'-l rus --oem 1 --psm 3 '  \
                      f'--tessdata-dir {ROOT_DIR}/utility/tessdata/default -c tessedit_char_blacklist={TESSERACT_BLACKLIST}'  # 3 7
TESSERACT_CONF_MAIN = f'-l rus --oem 1 --psm 3 '  \
                      f'--tessdata-dir {ROOT_DIR}/utility/tessdata/default -c tessedit_char_blacklist={TESSERACT_BLACKLIST}'  # 3 7
TESSERACT_CONF_DIGITS = f'-l eng --oem 1 -c tessedit_char_whitelist=0123456789.,-=₽ --psm 6 -c tessedit_char_blacklist={TESSERACT_BLACKLIST}'  # 4 6 7 8

TESSERACT_CONF_MAIN_WAITLIST = '-l eng --oem 1 --psm 3 ' \
                               '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz.-><°' \
                               f'--tessdata-dir {ROOT_DIR}/utility/tessdata'  # 3 7
TESSERACT_CONF_SYMBOLS = f'-l eng --oem 1 -c tessedit_char_whitelist=-> -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 6'
TESSERACT_CONF_IN_CIRCLE = f'-l eng --oem 1 -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 9'

resize_coeffs = [4, 6, 8]
easyocr_reader = easyocr.Reader(['ru'])


def prepared_img(cropped: np.ndarray, resize_coeff, is_digits: bool, is_bold: bool) -> np.ndarray:
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fy=resize_coeff, fx=resize_coeff, interpolation=cv2.INTER_LINEAR)

    if is_digits:
        ret, thresh = cv2.threshold(resized, 220, 255, 0)  # , cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    elif is_bold:
        ret, thresh = cv2.threshold(resized, 220, 255, 0)  # , cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        kernel_size = 5
        morph_kernel = np.ones((kernel_size, kernel_size))
        thresh = cv2.dilate(thresh, kernel=morph_kernel, iterations=1)
    else:
        blur = cv2.medianBlur(resized, 5)

        kernel_size = 3
        morph_kernel = np.ones((kernel_size, kernel_size))
        erode_img1 = cv2.erode(blur, kernel=morph_kernel, iterations=1)

        sharp_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpen_img = cv2.filter2D(erode_img1, ddepth=-1, kernel=sharp_filter)

        blur1 = cv2.medianBlur(sharpen_img, 3)

        ret, thresh = cv2.threshold(blur1, 220, 255, 0)#, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        # dilate_img1 = cv2.dilate(thresh, kernel=morph_kernel, iterations=1)

    # cv2.imshow("Test", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return thresh


def _get_tesseract_resp(cropped: np.ndarray,
                        resize_coeff: int,
                        config,
                        is_digits: bool,
                        is_bold: bool,
                        quality_min: int,
                        ) -> TesseractResp:
    """
    parses the cropped image with the Tesseract library
    :param cropped: np.ndarray - original cropped image
    :param resize_coeff: int - picture magnification factor
    :param config: str - Tesseract config
    :return:  TesseractResp
    """
    thresh = prepared_img(cropped, resize_coeff, is_digits, is_bold)

    # tesseract
    word = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=config)
    text = ''
    conf = 0
    sum_conf = 0
    count_of_words = 0
    print(word["text"])  #TODO DEBUG ONLY
    print(word["conf"])
    for i in range(len(word["text"])):
        txt = word['text'][i]
        cnf = word["conf"][i]
        if txt != '':
            count_of_words += 1
            sum_conf = sum_conf + cnf
            conf = sum_conf / count_of_words
            text = text + txt + ' '

    text, conf = (text.strip(), conf) if conf > quality_min else ('', 0)
    # print('99999999999999999999999', text, conf, resize_coeff)
    return TesseractResp(text=text, conf=conf, resize_coeff=resize_coeff, frame=thresh)


def _get_text_by_max_conf(results) -> TesseractResp:
    """
    gets the text at maximum confidence
    :param results: list[TesseractResp]
    :return: TesseractResp
    """
    max_conf = max([r.conf for r in results])
    tesseract_resp = [r for r in results if r.conf == max_conf][0]
    return tesseract_resp


def _get_results(config: str,
                 cropped: np.ndarray,
                 is_digits: bool,
                 is_bold: bool,
                 quality: int,
                 quality_min: int,
                 ) -> Tuple[List[TesseractResp], int]:
    """
    gets data for each image zoom
    :param config: str - tesseract config
    :param cropped: np.ndarray - original cropped image
    :return: Tuple[List[TesseractResp], int] - with count of pass
    """
    results = []
    count = 0
    for resize_coeff in resize_coeffs:
        count += 1
        tesseract_resp: TesseractResp = _get_tesseract_resp(cropped, resize_coeff, config, is_digits, is_bold, quality_min)
        results.append(tesseract_resp)
        if tesseract_resp.conf > quality:
            break
    return results, count


def _parse_with_easy_ocr(cropped: np.ndarray, is_bold: bool) -> tuple:
    for resize_coeff in [2, 4]:
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fy=resize_coeff, fx=resize_coeff, interpolation=cv2.INTER_LINEAR)
        if is_bold:
            kernel_size = 5
            morph_kernel = np.ones((kernel_size, kernel_size))
            resized = cv2.dilate(resized, kernel=morph_kernel, iterations=1)
        result1 = easyocr_reader.readtext(resized, detail=1)
        filtered_result1 = [t for t in result1 if t[2] > EASY_OCR_CONF]
        concat_res = ' '.join([t[1] for t in filtered_result1])
        print('Easy OCR:', result1)
        resp = TesseractResp(concat_res, 90, 2, cropped)
        if concat_res.replace(' ', '') != '':
            return [resp], 1
    return [TesseractResp('', 0, 2, cropped)], 1


def _get_results_by_tesseract_configs(cropped: np.ndarray) -> tuple:
    """
    If the result is not found, changes the tesseract configuration
    :param cropped: np.ndarray - original cropped image
    :return: tuple(list[TesseractResp], int) - with sum of count of pass
    """
    results = []
    cropped_origin = np.copy(cropped)
    results1, count1 = _get_results(TESSERACT_CONF_MAIN, cropped, False, False,
                                   TESSERACT_QUALITY, TESSERACT_QUALITY_MIN)

    count2 = 0
    res1 = _get_text_by_max_conf(results1)
    results2 = []
    if res1.conf < 90: # or len(res.text.replace(' ', '')) < letters_number:
        results2, count2 = _get_results(TESSERACT_CONF_DIGITS, cropped, True, False,
                                       TESSERACT_DIGITS_QUALITY, TESSERACT_DIGITS_QUALITY_MIN)

    h, w, _ = np.shape(cropped)
    cut_cropped: np.ndarray = cropped[0:h, 0:int(w - w*0.2)]
    res2 = _get_text_by_max_conf(results2) if results2 else None
    results3 = []
    count4 = 0
    if (res2 is None or res2.conf < 90) and (len(res1.text) > 0 and res1.text.replace(' ', '').lower()[-1] == 'р'):
        results3, count4 = _get_results(TESSERACT_CONF_DIGITS, cut_cropped, True, False,
                                       TESSERACT_DIGITS_QUALITY, TESSERACT_DIGITS_QUALITY_MIN)

    results = [_get_text_by_max_conf(results2 + results1 + results3)]

    # cut_cropped: np.ndarray = cropped[0:h, int(w/2.3):w]
    # count3 = 0
    # if _get_text_by_max_conf(results).conf == 0:
    #     results, count3 = _get_results(TESSERACT_CONF_DIGITS, cut_cropped, True,
    #                                    TESSERACT_DIGITS_QUALITY, TESSERACT_DIGITS_QUALITY_MIN,
    #                                    letters_number)

    count5 = 0
    text = _get_text_by_max_conf(results).text.strip() if results else ""
    if text == '':
        results, count5 = _get_results(TESSERACT_CONF_DEFAULT, cropped_origin, True, False,
                                       TESSERACT_QUALITY, TESSERACT_QUALITY_MIN)

    count6 = 0
    if not results or _get_text_by_max_conf(results).conf == 0:
        results, count6 = _parse_with_easy_ocr(cropped, False)

    count7 = 0
    if not results or _get_text_by_max_conf(results).conf == 0:
        results, count7 = _parse_with_easy_ocr(cropped, True)

    count = 0 #count1 + count2 + count5 # + count3 + count4

    # if get_text_by_max_conf(results)[1] == 0:
    #     results = get_results(TESSERACT_CONF_SYMBOLS)

    return results, count


@print_time_of_script
def get_img_text_by_contours(img: np.ndarray,
                             rectangles,
                             from_box_debug: int = None,
                             to_box_debug: int = None,
                             ) -> [RectangleData]:
    """
    cuts out areas from original image, gets text from areas
    :param img:np.ndarray - original frame
    :param rectangles:list[RectangleData] - without text
    :param from_box_debug: int - DEBUG ONLY
    :param to_box_debug: int - DEBUG ONLY
    :return:list[RectangleData] - with text
    """
    rectangles_txt = []
    count = 0
    for r in reversed(rectangles):
        count += 1
        if from_box_debug and count < from_box_debug:
            continue
        if to_box_debug and count > to_box_debug:
            break
        cropped: np.ndarray = img[r.y:r.y + r.h, r.x:r.x + r.w]
        # saving(ROOT_DIR + '/tests/imgs/result', f"{count}_{''}_{time.time()}", '', cropped, False)
        results, count_of_pass = _get_results_by_tesseract_configs(cropped)
        text, conf, r_coef, frame = _get_text_by_max_conf(results) if results else ("", 0, 0, np.ndarray([]))

        text = fix_word(text)

        #DEBUG
        # if save_cropped_img_path_debug:
            # _logger.debug(f"11111111111111111111111 {text}, conf={conf}, count_of_pass={count_of_pass}")
        saving(ROOT_DIR + '/tests/imgs/result', f"{count}_{text}_{time.time()}", text, cropped, False)

        r.text = text
        rectangles_txt.append(r)
        # if text != '':
        #     r.text = text
        #     rectangles_txt.append(r)

    return rectangles_txt
