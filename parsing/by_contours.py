import logging
import queue
import signal
import subprocess
import threading
import time
from typing import List, Tuple

import cv2
import easyocr
import numpy as np
from pytesseract import pytesseract

from definition import ROOT_DIR
from parsing.post_process import fix_word, create_str_from_frequency_dict, create_frequency_dict
from utility.decors.prdecorators import print_time_of_script, timeout
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
TESSERACT_CONF_DIGITS = f'-l eng --oem 1 -c tessedit_char_whitelist=*№0123456789.,-₽ --psm 6 -c tessedit_char_blacklist={TESSERACT_BLACKLIST}'  # 4 6 7 8

TESSERACT_CONF_MAIN_WAITLIST = '-l eng --oem 1 --psm 3 ' \
                               '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz.-><°' \
                               f'--tessdata-dir {ROOT_DIR}/utility/tessdata'  # 3 7
TESSERACT_CONF_SYMBOLS = f'-l eng --oem 1 -c tessedit_char_whitelist=-> -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 6'
TESSERACT_CONF_IN_CIRCLE = f'-l eng --oem 1 -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 9'

resize_coeffs = [4, 6, 8]
easyocr_reader = easyocr.Reader(['ru'])


def _enlarge_image_canvas(gray: np.ndarray) -> np.ndarray:
    """
    enlargement of the canvas for better recognition
    :param gray:np.ndarray
    :return:np.ndarray - increased
    """
    h, w = gray.shape
    add_h = int(h * 0.2)
    add_w = int(w * 0.2)
    count_of_iter = add_w if add_w > add_h else add_h
    arr_res = np.ndarray
    for i in range(count_of_iter):
        if i == 0:
            h, w = gray.shape
            if add_h > 0:
                arr_res = np.insert(gray, [0, h], 255, axis=0)
                add_h -= 1
            if add_w > 0:
                arr_res = np.insert(arr_res, [0, w], 255, axis=1)
                add_w -= 1
        else:
            h, w = arr_res.shape
            if add_h > 0:
                arr_res = np.insert(arr_res, [0, h], 255, axis=0)
                add_h -= 1
            if add_w > 0:
                arr_res = np.insert(arr_res, [0, w], 255, axis=1)
                add_w -= 1
    return arr_res


def prepared_img(cropped: np.ndarray, resize_coeff, is_digits: bool, is_bold: bool) -> np.ndarray:
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fy=resize_coeff, fx=resize_coeff, interpolation=cv2.INTER_LINEAR)
    resized = _enlarge_image_canvas(resized)

    if is_digits:
        ret, thresh = cv2.threshold(resized, 220, 255, 0)  # , cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    elif is_bold:
        kernel_size = 3
        morph_kernel = np.ones((kernel_size, kernel_size))
        sharp_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpen_img = cv2.filter2D(resized, ddepth=-1, kernel=sharp_filter)
        dilate = cv2.dilate(sharpen_img, kernel=morph_kernel, iterations=1)

        ret, thresh = cv2.threshold(sharpen_img, 170, 255, 0)  # , cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
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
    _logger.info(word["text"])  #TODO DEBUG ONLY
    _logger.info(word["conf"])
    for i in range(len(word["text"])):
        txt = word['text'][i]
        cnf = word["conf"][i]
        if txt != '':
            count_of_words += 1
            sum_conf = sum_conf + cnf
            conf = sum_conf / count_of_words
            text = text + txt + ' '

    text, conf = (text.strip(), conf) if conf > quality_min else ('', 0)
    results = [w for w in word["text"] if w != '']
    # print('99999999999999999999999', text, conf, resize_coeff)
    return TesseractResp(text=text, conf=conf, resize_coeff=resize_coeff, frame=thresh, results=results)


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
        resized = _enlarge_image_canvas(resized)
        if is_bold:
            kernel_size = 5
            morph_kernel = np.ones((kernel_size, kernel_size))
            resized = cv2.dilate(resized, kernel=morph_kernel, iterations=1)

        result1 = []
        temp_queue = queue.Queue()
        def easy_ocr_func(q, image, reader):
            res = reader.readtext(image=image, detail=1)
            q.put(res)
        t = threading.Thread(target=easy_ocr_func, args=(temp_queue, resized, easyocr_reader))
        t.start()

        try:
            result1 = temp_queue.get(timeout=2)
        except Exception:
            _logger.warning("EASY OCR TIMEOUT")

        filtered_result1 = [t for t in result1 if t[2] > EASY_OCR_CONF]
        concat_res = ' '.join([t[1] for t in filtered_result1])
        _logger.info(f'Easy OCR: {result1}')
        resp = TesseractResp(concat_res, 90, 2, cropped, [])
        if concat_res.replace(' ', '') != '':
            return [resp], 1
    return [TesseractResp('', 0, 2, cropped, [])], 1


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
    if res1.conf < 94: # or len(res.text.replace(' ', '')) < letters_number:
        results2, count2 = _get_results(TESSERACT_CONF_DIGITS, cropped, True, False,
                                       TESSERACT_DIGITS_QUALITY, TESSERACT_DIGITS_QUALITY_MIN)

    results = [_get_text_by_max_conf(results2 + results1)]

    count5 = 0
    res5 = _get_text_by_max_conf(results) #.text.strip() if results else ""
    results4 = []
    if res5 is None or (res5 and res5.conf < 94):
        results, count5 = _get_results(TESSERACT_CONF_DEFAULT, cropped_origin, True, False,
                                       TESSERACT_QUALITY, TESSERACT_QUALITY_MIN)

    res_text = ''
    res = _get_text_by_max_conf(results) if results else None
    if res is None or res.conf < 90:
        lm = lambda arr: [r.results for r in arr]
        tess_arr = lm(results) + lm(results1) + lm(results2)
        tess_arr = sorted(tess_arr, key=lambda a: len(a), reverse=True)
        res_text = create_str_from_frequency_dict(create_frequency_dict(tess_arr), tess_arr)
        print('11111111111111111111111111111111111111111111', res_text)

    if res_text.strip() != '':
        results = [TesseractResp(res_text, 90, 2, cropped, [])]

    count6 = 0
    if not results or _get_text_by_max_conf(results).conf == 0:
        results, count6 = _get_results(TESSERACT_CONF_DEFAULT, cropped_origin, False, True,
                                       TESSERACT_QUALITY, TESSERACT_QUALITY_MIN)

    count6 = 0
    if not results or _get_text_by_max_conf(results).conf == 0:
        results, count6 = _parse_with_easy_ocr(cropped, False)
    print('66666666666666666666666666666666666')

    count7 = 0
    if not results or _get_text_by_max_conf(results).conf == 0:
        results, count7 = _parse_with_easy_ocr(cropped, True)

    count = 0 #count1 + count2 + count5 # + count3 + count4

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
        h, w, z = cropped.shape
        if h > 0 and w > 0 and z > 0:
            results, count_of_pass = _get_results_by_tesseract_configs(cropped)
            text, conf, r_coef, frame, _ = _get_text_by_max_conf(results) if results else ("", 0, 0, np.ndarray([]))

            text = fix_word(text)

            #DEBUG
            # if save_cropped_img_path_debug:
                # _logger.debug(f"11111111111111111111111 {text}, conf={conf}, count_of_pass={count_of_pass}")
            #saving(ROOT_DIR + '/tests/imgs/result', f"{count}_{text}_{time.time()}", text, cropped, False)

            r.text = text
            rectangles_txt.append(r)
        else:
            _logger.warning(f"Failure to process cropped image, wrong shape <{cropped.shape}>")

    return rectangles_txt
