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
class AlfaSbpType(BaseCheckType,
                  RecipientName,
                  RecipientPhone,
                  SenderCardNumber,
                  ):
    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        texts = [replace_spaces(r.text).lower() for r in rects]
        keys = ['идбанкаполучателя']
        for key in keys:
            for t in texts:
                if key in t:
                    break
            else:
                return False
        else:
            return AlfaSbpType(rects, img).build

    @staticmethod
    def _parse_next_field_by_field_name(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(rects)):
                    curr_rect = rects[i]

                    if field_name in curr_rect:
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

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет отправителя', 'Счёт отправителя']
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
        DOC_NUMBER = 'Идентификатор'
        self.document_number = self._parse_next_field_by_field_name([DOC_NUMBER], self.rects)

    @property
    def build(self):
        self.parse_recipient_name()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        self.parse_sender_card_number()
        return self