import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone, SBPID
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import replace_spaces, fix_amount, clear_card_number
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class VTBType(BaseCheckType,
              SenderName,
              SenderCardNumber,
              RecipientName,
              RecipientPhone,
              SBPID,
              ):
    bank = BankType.VTB.value

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

    def _parse_field(self, field_names: List[str]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]

                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():

                        if field_name == 'операции в СБП':
                            numsbp_rects = []
                            for r in self.rects:
                                cx, cy, ch, cw = curr_rect.x, curr_rect.y, curr_rect.h, curr_rect.w
                                if cy - ch/2 < r.y < cy + ch*1.5 and r.x > cx + cw:
                                    numsbp_rects.append(r)
                            return ''.join([r.text for r in numsbp_rects])

                        else:
                            h = curr_rect.h / 2
                            prev_rect = self.rects[i - 1]
                            if curr_rect.y - h < prev_rect.y < curr_rect.y + h:
                                return self.rects[i - 1].text

                            next_rect = self.rects[i + 1]
                            if curr_rect.y - h < next_rect.y < curr_rect.y + h:
                                return self.rects[i + 1].text
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = ['Имя плательщика', 'плательщика Имя']
        self.sender_name = self._parse_field(SENDER_NAME)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет']
        res = self._parse_field(SENDER_CARD_NUMBER)
        self.sender_card_number = clear_card_number(res)

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
        self.amount = fix_amount(res)

    def parse_sbp_id(self):
        SBP_ID = 'операции в СБП'
        self.sbp_id = self._parse_field([SBP_ID])

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_sender_card_number()
        self.parse_recipient_name()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_sbp_id()
        return self