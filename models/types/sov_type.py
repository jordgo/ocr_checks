import dataclasses
import logging
from dataclasses import dataclass
from typing import List, Callable

import cv2
import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone, SBPID, DocNumber
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.parsing_func import process_rectangle_img
from parsing.post_process import replace_spaces, fix_amount, clear_card_number, extract_last, extract_except_from_start, \
    neighboring_rect, extract_last_numbers
from utility.comparison.comparation import is_different_text
from utility.rectangle_utils.prepare_img import cut_img_by_rect

_logger = logging.getLogger("app")


@dataclass
class SovType(BaseCheckType,
              SenderCardNumber,
              RecipientCardNumber,
              DocNumber,
              ):
    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        h, w, _ = img.shape
        key = 'совкомбанк'
        for r in rects:
            if key in replace_spaces(r.text).lower() and r.y < h*0.3:
                return SovType(rects, img).build
        return False

    def _parse_field(self, field_names: List[str], extract_func: Callable) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]
                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
                        return extract_func(replace_spaces(self.rects[i].text))
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет отправителя', 'отправителя Счет']
        res = self._parse_field(SENDER_CARD_NUMBER, extract_last)
        try:
            res = clear_card_number(res)[-4:]
        except Exception:
            pass
        self.sender_card_number = res

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['карту']
        res = self._parse_field(RECIPIENT_CARD_NUMBER, _extract_recipient_card)
        try:
            res = clear_card_number(res)[-4:]
        except Exception:
            pass
        self.recipient_card_number = res

    def parse_check_date(self):
        DATE = 'Дата'
        self.check_date = self._parse_field([DATE], extract_last_numbers(2))

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA, lambda res: ''.join([s for s in res if s.isdigit()]))
        self.amount = fix_amount(res)

    def parse_document_number(self):
        DOC_NUMBER = 'документа'
        res = self._parse_field([DOC_NUMBER], extract_last)
        self.document_number = res #''.join([s for s in res if s.isdigit()])

    @property
    def build(self):
        self.parse_sender_card_number()
        self.parse_recipient_card_number()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        return self


def _extract_recipient_card(raw_str: str) -> str:
    try:
        res = raw_str.split('карту')[1]
        return ''.join([s for s in res if s.isdigit()])
    except Exception as e:
        _logger.warning(f"Failure to parse RecipientCard str: <{raw_str}>, error: {e}")
        return NOT_DEFINED