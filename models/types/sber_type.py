import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderCardNumber, SenderName, RecipientName, RecipientCardNumber, DocNumber
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import fix_amount, clear_card_number, replace_spaces
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class SberType(BaseCheckType,
               SenderCardNumber,
               SenderName,
               RecipientName,
               RecipientCardNumber,
               DocNumber,
               ):
    bank = BankType.SBER.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        texts = [r.text.lower().replace(' ', '') for r in rects]
        keys = ['чекпооперации', 'почекоперации', 'пооперациичек', 'чекоперациипо', 'операциичекпо', 'операциипочек']
        for key in keys:
            if key in texts:
                return SberType(rects, img).build
            else:
                return False

    @staticmethod
    def _parse_field(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(rects)):
                    if replace_spaces(field_name).lower() in replace_spaces(rects[i].text).lower():
                        return rects[i + 1].text
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = ['ФИО отправителя', 'отправителя ФИО']
        self.sender_name = self._parse_field(SENDER_NAME, self.rects)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет отправителя', 'отправителя Счет']
        res = self._parse_field(SENDER_CARD_NUMBER, self.rects)
        self.sender_card_number = clear_card_number(res)

    def parse_recipient_name(self):
        RECIPIENT_NAME = ['ФИО получателя', 'получателя ФИО']
        self.recipient_name = self._parse_field(RECIPIENT_NAME, self.rects)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['карты получателя', 'счета получателя', 'получателя карты', 'получателя счета']
        res = self._parse_field(RECIPIENT_CARD_NUMBER, self.rects)
        self.recipient_card_number = clear_card_number(res)

    def parse_check_date(self):
        PREV_FIELD = ['чек по операции']
        self.check_date = self._parse_field(PREV_FIELD, self.rects)

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA, self.rects)
        self.amount = fix_amount(res)

    def parse_document_number(self):
        DOC_NUMBER = 'документа'
        self.document_number = self._parse_field([DOC_NUMBER], self.rects)

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_recipient_card_number()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        return self


