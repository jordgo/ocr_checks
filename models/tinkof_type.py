import logging
from dataclasses import dataclass
from typing import List

from models.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class TinkoffType(BaseCheckType):
    def __init__(self, rects: List[RectangleData]):
        self.rects = rects

    @staticmethod
    def create(rects: List[RectangleData]):
        texts = [r.text.lower().replace(' ', '') for r in rects]
        if 'тинькофф' in texts:
            return TinkoffType(rects).build
        else:
            return False

    @staticmethod
    def _parse_next_field_by_field_name(field_names: List[str], rects: List[RectangleData]) -> str:
        for field_name in field_names:
            try:
                for i in range(len(rects)):
                    curr_rect = rects[i]
                    if field_name == 'Квитанция №' and 'Квитанция №' in curr_rect.text:
                        return curr_rect.text.replace('Квитанция №', '').strip()

                    if not is_different_text(curr_rect.text, field_name, 7):
                        if field_name == 'тинькофф':
                            return rects[i + 1].text

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
        SENDER_NAME = 'Отправитель'
        self.sender_name = self._parse_next_field_by_field_name([SENDER_NAME], self.rects)

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['']
        self.sender_card_number = NOT_DEFINED

    def parse_recipient_name(self):
        RECIPIENT_NAME = 'Получатель'
        self.recipient_name = self._parse_next_field_by_field_name([RECIPIENT_NAME], self.rects)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['Карта получателя', 'Телефон получателя']
        self.recipient_card_number =  self._parse_next_field_by_field_name(RECIPIENT_CARD_NUMBER, self.rects)

    def parse_check_date(self):
        PREV_FIELD = 'тинькофф'
        self.check_date = self._parse_next_field_by_field_name([PREV_FIELD], self.rects)

    def parse_amount(self):
        SUMMA = ['Сумма']
        self.amount = self._parse_next_field_by_field_name(SUMMA, self.rects)

    def parse_document_number(self):
        DOC_NUMBER = 'Квитанция №'
        self.document_number = self._parse_next_field_by_field_name([DOC_NUMBER], self.rects)