import logging
import re
from dataclasses import dataclass
from typing import List, Callable

import numpy as np

from models.types.additional_fields import SenderCardNumber, SenderName, RecipientName, RecipientPhone, DocNumber
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
# from parsing.parsing_func import process_rectangle_img
from parsing.post_process import replace_spaces, fix_amount, extract_last, extract_except_from_start, extract_digits
from utility.comparison.comparation import is_different_text
from utility.rectangle_utils.search_rect import find_rect_opt

_logger = logging.getLogger("app")


@dataclass
class RaiffaizenType(BaseCheckType,
                     SenderCardNumber,
                     SenderName,
                     RecipientName,
                     RecipientPhone,
                     DocNumber,
                     ):
    bank = BankType.RAIFAIZEN.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        h, w, _ = img.shape
        key = 'райффайзен'
        for r in rects:
            if key in replace_spaces(r.text).lower() and r.y < h*0.3:
                return RaiffaizenType(rects, img).build
        return False

    def _parse_field(self, field_names: List[str],
                     extract_func: Callable,
                     ) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    if field_name in self.rects[i].text:
                        if field_name == 'Получатель' or \
                           field_name == 'Прошу' or field_name == 'осуществить' or field_name == 'моего' or \
                           field_name == 'Заявление' or field_name == 'рублевый' or field_name == 'рублёвый':
                            return extract_func(replace_spaces(self.rects[i + 1].text))
                        return extract_func(replace_spaces(self.rects[i].text))
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = ['Плательщик']
        self.sender_name = self._parse_field(SENDER_NAME, extract_except_from_start(1))

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Прошу', 'осуществить', 'моего']
        self.sender_card_number = self._parse_field(SENDER_CARD_NUMBER, extract_card_number)

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'Получатель'
        self.recipient_name = self._parse_field([RECIPIENT_NAME], extract_except_from_start(1))

    def parse_check_date(self):
        DATE = 'Дата'
        # date_rect_opt = find_rect_opt(self.rects, DATE)
        # if date_rect_opt is not None:
        #     res = process_rectangle_img(self.img, date_rect_opt)
        #     self.check_date = _fix_time_of_str(extract_except_from_start(1)(res))
        # else:
        #     self.check_date = NOT_DEFINED
        res = self._parse_field([DATE], extract_except_from_start(1))
        self.check_date = _fix_time_of_str(res)

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA, _extract_amount)
        self.amount = fix_amount(res)

    def parse_document_number(self):
        DOC_NUMBER = ['Заявление', 'рублевый', 'рублёвый']
        self.document_number = self._parse_field(DOC_NUMBER, _extract_number)

    def parse_recipient_phone(self):
        PHONE = ['Телефон']
        self.recipient_phone = self._parse_field(PHONE, extract_last)

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        self.parse_recipient_phone()
        return self


def _fix_time_of_str(raw_str: str) -> str:
    arr = raw_str.split(' ')
    if len(arr) > 1:
        time_str = arr[-1].replace(':', '')
        if len(time_str) == 6:
            time_arr: List[str] = re.findall('(.{%s}|.+$)' % 2, time_str)
            time_str = ':'.join(time_arr)
            arr[-1] = time_str
        return ' '.join(arr)
    else:
        return raw_str


def _fix_time(raw_str: str) -> str:
    time_str = raw_str.replace(':', '')
    if len(time_str) == 6:
        time_arr: List[str] = re.findall('(.{%s}|.+$)' % 2, time_str)
        time_str = ':'.join(time_arr)
    return  time_str


def _fix_number(raw_str: str) -> str:
    return  'N' + ''.join(i for i in raw_str if not i.isalpha())


def _cut_from_first_digit(raw_str: str) -> str:
    try:
        first_digit_pos = next(i for i, c in enumerate(raw_str) if c.isdigit())
    except StopIteration:
        first_digit_pos = 0

    if first_digit_pos > 0:
        res = raw_str[first_digit_pos:]
    else:
        res = raw_str
    return res


def _extract_number(raw_str: str) -> str:
    str_origin = replace_spaces(raw_str)
    cut_str = _cut_from_first_digit(str_origin)
    res_arr: List[str] = cut_str.split(' ')
    if len(res_arr) >= 5:
        fixed_time = _fix_time(res_arr[-1])
        res_arr[-1] = fixed_time
        fixed_number = _fix_number(res_arr[0])
        res_arr[0] = fixed_number
        return ' '.join(res_arr)
    return NOT_DEFINED


def _extract_amount(raw_str: str) -> str:
    str_origin = replace_spaces(raw_str)
    arr = str_origin.split(' ')
    if len(arr) > 2:
        res = arr[2]
    else:
        res = NOT_DEFINED
    return res


def extract_card_number(raw_str: str) -> str:
    arr = raw_str.split(' ')
    digits = []
    for s in arr:
        for w in s:
            if not w.isdigit():
                break
        else:
            digits.append(s)
    if len(digits) > 0:
        d_sorted = sorted(digits, key=lambda d: len(d), reverse=True)
        return d_sorted[0]
    return NOT_DEFINED
