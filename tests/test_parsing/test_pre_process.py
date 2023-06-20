import cv2
import numpy as np
import pytest

from definition import ROOT_DIR
from parsing.by_contours import _get_results_by_tesseract_configs, _get_text_by_max_conf


@pytest.mark.parametrize("img_path, exp", [
    (ROOT_DIR + "/tests/imgs/check_by_operation.png", "Чек по операции"),
    (ROOT_DIR + "/tests/imgs/opercia.png", "Операция"),
    (ROOT_DIR + "/tests/imgs/3714.png", "3714"),
    (ROOT_DIR + "/tests/imgs/8124.png", "8124"),
    (ROOT_DIR + "/tests/imgs/summa.png", "320,00 ₽"),
    (ROOT_DIR + "/tests/imgs/summa_pere.png", "Сумма перевода"),
    (ROOT_DIR + "/tests/imgs/363885.png", "363885"),
    (ROOT_DIR + "/tests/imgs/alex_vas.png", "Александр Васильевич П."),
    (ROOT_DIR + "/tests/imgs/tinkof_date.png", "05.06.2023 02"),  #02:33:24
    (ROOT_DIR + "/tests/imgs/tinkoff.png", "тинькофф"),
])
def test_prepared_img(img_path, exp):
    img = cv2.imread((img_path))
    res = _get_results_by_tesseract_configs(img)
    text, conf, r_coef, frame = _get_text_by_max_conf(res[0]) if res[0] else ("", 0, 0, np.ndarray([]))


    assert text.lower().replace(" ", '') == exp.lower().replace(" ", '')