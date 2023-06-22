import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import replace_spaces
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class VTBType(BaseCheckType,
              SenderName,
              SenderCardNumber,
              RecipientName,
              RecipientPhone,
              ):
    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        h, w, _ = img.shape
        key = 'втб'
        for r in rects:
            if key in replace_spaces(r.text).lower() and r.y < h*0.3:
                return VTBType(rects, img).build
        return False

    @staticmethod
    def _parse_next_field_by_field_name(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(rects)):
                    curr_rect = rects[i]

                    if field_name in curr_rect.text:

                        if field_name == 'операции в СБП':
                            numsbp_rects = []
                            for r in rects:
                                cx, cy, ch, cw = curr_rect.x, curr_rect.y, curr_rect.h, curr_rect.w
                                if cy - ch/2 < r.y < cy + ch*1.5 and r.x > cx + cw:
                                    numsbp_rects.append(r)
                            return ''.join([r.text for r in numsbp_rects])

                        else:
                            h = curr_rect.h / 2
                            prev_rect = rects[i - 1]
                            if curr_rect.y - h < prev_rect.y < curr_rect.y + h:
                                return rects[i - 1].text

                            next_rect = rects[i + 1]
                            if curr_rect.y - h < next_rect.y < curr_rect.y + h:
                                return rects[i + 1].text
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = ['Имя плательщика', 'Имя плательшика']
        self.sender_name = self._parse_next_field_by_field_name(SENDER_NAME, self.rects)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет', 'Счёт']
        self.sender_card_number = self._parse_next_field_by_field_name(SENDER_CARD_NUMBER, self.rects)

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'Получатель'
        self.recipient_name = self._parse_next_field_by_field_name([RECIPIENT_NAME], self.rects)

    def parse_recipient_phone(self):
        PHONE = ['Телефон']
        self.recipient_phone = self._parse_next_field_by_field_name(PHONE, self.rects)

    def parse_check_date(self):
        DATE = 'Дата'
        self.check_date = self._parse_next_field_by_field_name([DATE], self.rects)

    def parse_amount(self):
        SUMMA = ['Сумма']
        self.amount = self._parse_next_field_by_field_name(SUMMA, self.rects)

    def parse_document_number(self):
        DOC_NUMBER = 'операции в СБП'
        self.document_number = self._parse_next_field_by_field_name([DOC_NUMBER], self.rects)

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        return self