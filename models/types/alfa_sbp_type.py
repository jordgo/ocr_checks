import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone, SBPID
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import replace_spaces, fix_amount, neighboring_rect
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class AlfaSbpType(BaseCheckType,
                  RecipientName,
                  RecipientPhone,
                  SenderCardNumber,
                  SBPID,
                  ):
    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        texts = [replace_spaces(r.text).lower() for r in rects]
        keys = ['ИД Банка получателя']
        for key in keys:
            for t in texts:
                if key.replace(' ','').lower() in t.replace(' ','').lower():
                    break
            else:
                return False
        else:
            return AlfaSbpType(rects, img).build

    def _parse_field(self, field_names: List[str]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]

                    if field_name.replace(' ','').lower() in curr_rect.text.replace(' ','').lower():
                        neighb_rect = neighboring_rect(self.rects, curr_rect, i)
                        if neighb_rect is None:
                            return NOT_DEFINED
                        return neighb_rect.text
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет отправителя', 'отправителя Счет']
        self.sender_card_number = self._parse_field(SENDER_CARD_NUMBER)

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'Получатель'
        self.recipient_name = self._parse_field([RECIPIENT_NAME])

    def parse_recipient_phone(self):
        PHONE = ['Телефон']
        self.recipient_phone = self._parse_field(PHONE)

    def parse_check_date(self):
        DATE = 'Дата'
        self.check_date = self._parse_field([DATE])

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA)
        self.amount = ''.join([s for s in res if s.isdigit() or s == '.' or s == ',']).replace(' ','')

    def parse_sbp_id(self):
        SBP = 'Идентификатор'
        self.sbp_id = self._parse_field([SBP])

    @property
    def build(self):
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_sbp_id()
        return self