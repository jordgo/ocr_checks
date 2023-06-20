import logging
from dataclasses import dataclass
from typing import List

from models.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class SberType(BaseCheckType):
    def __init__(self, rects: List[RectangleData]):
        self.rects = rects

    @staticmethod
    def create(rects: List[RectangleData]):
        texts = [r.text.lower().replace(' ', '') for r in rects]
        if 'чекпооперации' in texts:
            return SberType(rects).build
        else:
            return False

    @staticmethod
    def _parse_next_field_by_field_name(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                # index = [r.text.lower().replace(' ', '') for r in rects].index(field_name.lower().replace(' ', '')) + 1
                # return rects[index].text
                for i in range(len(rects)):
                    if not is_different_text(rects[i].text, field_name, 7):
                        return rects[i + 1].text
            except ValueError:
                _logger.warning(f"Field <{field_name}> Not Found")
                continue
            except IndexError:
                _logger.warning(f"FieldValue of <{field_name}> Not Found")
                continue
        return NOT_DEFINED

    def parse_sender_name(self):
        SENDER_NAME = 'ФИО отправителя'
        self.sender_name = self._parse_next_field_by_field_name([SENDER_NAME], self.rects)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Счет отправителя', 'Счёт отправителя']
        self.sender_card_number = self._parse_next_field_by_field_name(SENDER_CARD_NUMBER, self.rects)

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'ФИО получателя'
        self.recipient_name = self._parse_next_field_by_field_name([RECIPIENT_NAME], self.rects)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['Номер карты получателя', 'номер счёта получателя', 'номер счета получателя']
        self.recipient_card_number = self._parse_next_field_by_field_name(RECIPIENT_CARD_NUMBER, self.rects)

    def parse_check_date(self):
        PREV_FIELD = 'Чек по операции'
        self.check_date = self._parse_next_field_by_field_name([PREV_FIELD], self.rects)

    def parse_amount(self):
        SUMMA = ['Сумма перевода', 'Сумма пере']
        self.amount = self._parse_next_field_by_field_name(SUMMA, self.rects)

    def parse_document_number(self):
        DOC_NUMBER = 'Номер документа'
        self.document_number = self._parse_next_field_by_field_name([DOC_NUMBER], self.rects)