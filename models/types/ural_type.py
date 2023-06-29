import dataclasses
import logging
from dataclasses import dataclass
from typing import List

import cv2
import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, SenderCardNumber, \
    RecipientPhone, SBPID, DocNumber
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.parsing_func import process_rectangle_img
from parsing.post_process import replace_spaces, fix_amount, clear_card_number, extract_last, extract_except_from_start, \
    neighboring_rect, extract_last_numbers
from utility.comparison.comparation import is_different_text
from utility.rectangle_utils.prepare_img import cut_img_by_rect

_logger = logging.getLogger("app")


@dataclass
class UralType(BaseCheckType,
               SenderName,
               RecipientName,
               RecipientPhone,
               SBPID,
               DocNumber,
              ):
    bank = BankType.URAL.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        h, w, _ = img.shape
        key = 'уралсиб'
        for r in rects:
            if key in replace_spaces(r.text).lower() and r.y < h*0.3:
                return UralType(rects, img).build
        return False

    def _parse_field(self, field_names: List[str]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]
                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
                        if field_name == 'Телефон':
                            return extract_except_from_start(2)(self.rects[i].text)
                        elif field_name == 'Дата' or field_name == 'Квитанция':
                            return extract_except_from_start(1)(self.rects[i].text)
                        else:
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

    def parse_sender_name(self):
        SENDER_NAME = ['Отправитель']
        self.sender_name = self._parse_field(SENDER_NAME)

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

    def parse_document_number(self):
        DOC_NUMBER = 'Квитанция'
        res = self._parse_field([DOC_NUMBER])
        self.document_number = ''.join([s for s in res if s.isdigit()])

    def parse_sbp_id(self):
        SBP = 'Идентификатор'
        self.sbp_id = self._parse_field([SBP])

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_recipient_name()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        self.parse_sbp_id()
        return self