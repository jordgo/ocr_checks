import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderCardNumber, TransactionNumberForRecipient, RecipientCardNumber, \
    DocNumber
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import fix_amount, replace_spaces
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class QiwiType(BaseCheckType,
               SenderCardNumber,
               TransactionNumberForRecipient,
               RecipientCardNumber,
               DocNumber):
    bank = BankType.QIWI.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        texts = [r.text.lower().replace(' ', '') for r in rects]
        keys = ['киви', 'кошелька']
        for key in keys:
            for t in texts:
                if key in t:
                    break
            else:
                return False
        else:
            return QiwiType(rects, img).build

    @staticmethod
    def _parse_next_field_by_field_name(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(rects)):
                    curr_rect = rects[i]

                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
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
        SENDER_CARD_NUMBER: List[str] = ['Списано']
        self.sender_card_number = self._parse_next_field_by_field_name(SENDER_CARD_NUMBER, self.rects)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['счета']
        self.recipient_card_number = self._parse_next_field_by_field_name(RECIPIENT_CARD_NUMBER, self.rects)

    def parse_check_date(self):
        CHECK_DATA = 'Дата'
        self.check_date = self._parse_next_field_by_field_name([CHECK_DATA], self.rects)

    def parse_amount(self):
        SUMMA = ['Итого']
        res = self._parse_next_field_by_field_name(SUMMA, self.rects)
        self.amount = fix_amount(res)

    def parse_document_number(self):
        DOC_NUMBER = ['квитанции']
        self.document_number = self._parse_next_field_by_field_name(DOC_NUMBER, self.rects)

    def parse_transaction_number_for_recipient(self):
        TRANSACTION_NUMBER = ['операции']
        self.transaction_number_for_recipient = self._parse_next_field_by_field_name(TRANSACTION_NUMBER, self.rects)

    @property
    def build(self):
        self.parse_sender_card_number()
        self.parse_recipient_card_number()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        self.parse_transaction_number_for_recipient()
        return self