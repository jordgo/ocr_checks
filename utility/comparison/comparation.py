import logging

import cv2
import numpy as np

_logger = logging.getLogger("app")


def pre_process(img: np.ndarray) -> np.ndarray:
    h, w, _ = img.shape
    coeff = 0.5
    resized = cv2.resize(img, (int(w*coeff), int(h*coeff)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    avg = gray.mean()
    ret, threshold_image = cv2.threshold(gray, avg, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    # save_to_dir.save_to_file(ROOT_DIR + f'/tests/results/frame_{time.time()}.png', threshold_image, is_img=True)

    return threshold_image


def get_diff_percentage_img(prev_img, current_img) -> float:
    if prev_img.shape != current_img.shape:
        return 100
    res = cv2.absdiff(prev_img, current_img)
    res = res.astype(np.uint8)
    percentage = (np.count_nonzero(res) * 1000) / res.size
    return percentage


def _clear_str(s: str) -> str:
    return s.replace(" ", "").replace("\n", "")


def prc_of_text_difference(txt1, txt2) -> int:
    count = 0
    max_len = len(txt2) if len(txt2) > len(txt1) else len(txt1)
    for i in range(max_len):
        try:
            if txt1[i].replace(" ", "").lower() != txt2[i].replace(" ", "").lower():
                count += 1
        except IndexError:
            count += 1

    diff_prc = int((count * 100) / max_len) if max_len else  0
    return diff_prc


def is_different_text(txt1, txt2, THRESHOLD_OF_TXT_PRC) -> bool:
    """check If the text is different from the previous one"""
    diff_prc = prc_of_text_difference(txt1, txt2)

    # _logger.debug(f"Text diff prc={diff_prc}, threshold={THRESHOLD_OF_TXT_PRC}")

    if diff_prc > THRESHOLD_OF_TXT_PRC:
        return True

    return False
