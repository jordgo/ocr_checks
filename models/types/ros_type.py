import dataclasses
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

import cv2
import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone, SBPID
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.parsing_func import process_rectangle_img
from parsing.post_process import replace_spaces, fix_amount, clear_card_number, extract_last, extract_except_from_start, \
    neighboring_rect, extract_last_numbers
from utility.comparison.comparation import is_different_text
from utility.rectangle_utils.prepare_img import cut_img_by_rect

_logger = logging.getLogger("app")


@dataclass
class RosType(BaseCheckType,
              SenderName,
              SenderCardNumber,
              RecipientName,
              RecipientPhone,
              RecipientCardNumber,
              SBPID,
              ):
    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        h, w, _ = img.shape
        key = 'росбанк'
        for r in rects:
            if key in replace_spaces(r.text).lower() and r.y < h*0.3:
                return RosType(rects, img).build
        return False

    def _parse_field(self, field_names: List[str]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]
                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
                        if field_name == 'Принято банком':
                            return self.rects[i + 1].text
                        elif field_name == 'назначение':
                            return extract_last_numbers(2)(self.rects[i].text)
                        elif 'Счет' in field_name:
                            target_rect = neighboring_rect(self.rects, curr_rect, i)
                            if target_rect is not None:
                                new_rect = dataclasses.replace(target_rect)
                                max_x = target_rect.x + target_rect.w
                                new_rect.x = target_rect.x + int(target_rect.w - target_rect.w*0.24)
                                new_rect.w = max_x - target_rect.x
                                res_text = process_rectangle_img(self.img, new_rect)
                                return res_text
                            else:
                                return NOT_DEFINED
                        else:
                            neighb_rect = neighboring_rect(self.rects, curr_rect, i)
                            if neighb_rect is None:
                                return NOT_DEFINED
                            return neighb_rect.text
            except ValueError as err:
                _logger.warning(f"Field <{field_name}> Not Found, err: <{err}>")
                continue
            except IndexError as err:
                _logger.warning(f"FieldValue of <{field_name}> Not Found, err: <{err}>")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = ['ФИО плательщика', 'плательщика ФИО']
        self.sender_name = self._parse_field(SENDER_NAME)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет плательщика', 'плательщика Счет']
        res = self._parse_field(SENDER_CARD_NUMBER)
        self.sender_card_number = clear_card_number(res)

    def parse_recipient_name(self):
        RECIPIENT_NAME = ['ФИО получателя', 'получателя ФИО']
        self.recipient_name = self._parse_field(RECIPIENT_NAME)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['Счет получателя', 'получателя Счет']
        res = self._parse_field(RECIPIENT_CARD_NUMBER)
        self.recipient_card_number = clear_card_number(res)

    def parse_recipient_phone(self):
        PHONE = ['Телефон получателя']
        self.recipient_phone = self._parse_field(PHONE)

    def parse_check_date(self):
        DATE = ['Принято банком', 'банком Принято']
        res: str = self._parse_field(DATE)
        self.check_date = res

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA)
        self.amount = fix_amount(res)

    def parse_sbp_id(self):
        SBP_ID = ['назначение']
        self.sbp_id = self._parse_field(SBP_ID)

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_recipient_phone()
        self.parse_recipient_card_number()
        self.parse_check_date()
        self.parse_amount()
        self.parse_sbp_id()
        return self