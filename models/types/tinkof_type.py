import datetime
import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderName, RecipientName, RecipientCardNumber, DocNumber, RecipientPhone
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.post_process import fix_amount, replace_spaces
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class TinkoffType(BaseCheckType,
                  SenderName,
                  RecipientName,
                  RecipientCardNumber,
                  RecipientPhone,
                  DocNumber,
                  ):
    bank = BankType.TINKOFF.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        texts = [r.text.lower().replace(' ', '') for r in rects]
        keys = ['тинькофф', 'статус', 'перевод']
        for key in keys:
            for t in texts:
                if key in t:
                    break
            else:
                return False
        else:
            return TinkoffType(rects, img).build

    def _parse_field(self, field_names: List[str]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]
                    if field_name == 'Квитанция №' and 'Квитанция №' in curr_rect.text:
                        return curr_rect.text.replace('Квитанция №', '').strip()

                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
                        if field_name == 'Итого':
                            for j in [1, 2]:
                                try:
                                    date = datetime.datetime.strptime(self.rects[i - j].text, '%d.%m.%Y %H:%M:%S')
                                    return date.strftime('%d.%m.%Y %H:%M:%S')
                                except Exception as e:
                                    _logger.warning(f'Failure to parse date from <{self.rects[i - j].text}>, error: {e}')
                                    continue
                            return NOT_DEFINED

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
        SENDER_NAME = 'Отправитель'
        self.sender_name = self._parse_field([SENDER_NAME])

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'Получатель'
        self.recipient_name = self._parse_field([RECIPIENT_NAME])

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['Карта получателя', 'получателя Карта']
        self.recipient_card_number =  self._parse_field(RECIPIENT_CARD_NUMBER)

    def parse_recipient_phone(self):
        PHONE = ['Телефон получателя']
        self.recipient_phone = self._parse_field(PHONE)

    def parse_check_date(self):
        DATE = 'Итого'
        self.check_date = self._parse_field([DATE])

    def parse_amount(self):
        SUMMA = ['Сумма']
        res = self._parse_field(SUMMA)
        self.amount = ''.join([s for s in res if s.isdigit() or s == '.' or s == ','])

    def parse_document_number(self):
        DOC_NUMBER = 'Квитанция №'
        self.document_number = self._parse_field([DOC_NUMBER])

    @property
    def build(self):
        self.parse_sender_name()
        self.parse_recipient_name()
        self.parse_recipient_card_number()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_document_number()
        return self