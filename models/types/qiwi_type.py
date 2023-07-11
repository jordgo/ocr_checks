import logging
from dataclasses import dataclass
from typing import List

import numpy as np

from models.types.additional_fields import SenderCardNumber, TransactionNumberForRecipient, RecipientCardNumber, \
    DocNumber, RecipientPhone, SBPID, Itogo, Commission
from models.types.bank_types import BankType
from models.types.base_check_type import BaseCheckType, NOT_DEFINED
from models.data_classes import RectangleData
from parsing.parsing_func import process_rectangle_img
from parsing.post_process import fix_amount, replace_spaces, neighboring_rect
from utility.comparison.comparation import is_different_text

_logger = logging.getLogger("app")


@dataclass
class QiwiType(BaseCheckType,
               SenderCardNumber,
               TransactionNumberForRecipient,
               RecipientCardNumber,
               RecipientPhone,
               SBPID,
               Itogo,
               Commission,
               DocNumber):
    bank = BankType.QIWI.value

    def __init__(self, rects: List[RectangleData], img: np.ndarray):
        self.rects = rects
        self.img = img

    @staticmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        # texts = [r.text.lower().replace(' ', '') for r in rects]
        h, w, _ = img.shape
        keys = ['киви', 'кошел']
        for key in keys:
            for r in rects:
                if key in r.text.lower().replace(' ', ''): # and r.y < h*0.3:
                    break
            else:
                return False
        else:
            return QiwiType(rects, img).build

    def _parse_field(self,
                     field_names: List[str],
                     default_word_count: int = None,
                     rectangle: RectangleData = None,
                     attempt_count=0
                     ) -> str:
        for field_name in field_names:
            try:
                for i in range(len(self.rects)):
                    curr_rect = self.rects[i]

                    if 'Идентификатор'.lower() in replace_spaces(curr_rect.text).lower() and (
                            (field_name == 'Идентификатор получателя' and (
                                    self.rects[i + 1].text == 'получателя' or
                                    self.rects[i + 2].text == 'получателя'
                            ))
                    ):
                        neighb_rect = neighboring_rect(self.rects, curr_rect, i)
                        if neighb_rect is None:
                            return NOT_DEFINED
                        return neighb_rect.text

                    if 'Идентификатор'.lower() in replace_spaces(curr_rect.text).lower() and (
                            (field_name == 'Идентификатор операции' and (
                                    self.rects[i + 1].text == 'операции' or
                                    self.rects[i + 2].text == 'операции'
                            ))
                    ):
                        neighb_rect_part1 = neighboring_rect(self.rects, curr_rect, i)
                        j = i + 1 if self.rects[i + 1].text == 'операции' else i + 2
                        neighb_rect_part2 = neighboring_rect(self.rects, self.rects[j], j)

                        if neighb_rect_part1 is None:
                            return NOT_DEFINED

                        neighb_rect_part2_txt = neighb_rect_part2.text if neighb_rect_part2 is not None else ''

                        return neighb_rect_part1.text + neighb_rect_part2_txt

                    if replace_spaces(field_name).lower() in replace_spaces(curr_rect.text).lower():
                        if field_name == 'Сумма':
                            print('==================================================================================', curr_rect.text)
                            return curr_rect.text

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

        if rectangle is not None and attempt_count < 1:
            _logger.warning(f"Field NOT FOUND <{field_names}>, "
                            f"trying again with default_word_count={default_word_count}"
                            f"rectangle={rectangle}")
            res_text = process_rectangle_img(self.img, rectangle, default_word_count)
            _logger.info(f"New Text <{res_text}>")
            for r in self.rects:
                if r == rectangle:
                    r.text = res_text

            attempt_count += 1
            return self._parse_field(field_names, default_word_count, rectangle, attempt_count)

        return NOT_DEFINED

    def parse_sender_card_number(self):
        SENDER_CARD_NUMBER: List[str] = ['Списано']
        self.sender_card_number = self._parse_field(SENDER_CARD_NUMBER)

    def parse_recipient_card_number(self):
        RECIPIENT_CARD_NUMBER = ['счета']
        self.recipient_card_number = self._parse_field(RECIPIENT_CARD_NUMBER)

    def parse_recipient_phone(self):
        PHONE = ['Идентификатор получателя']
        self.recipient_phone = self._parse_field(PHONE)

    def parse_check_date(self):
        CHECK_DATA = 'Дата'
        self.check_date = self._parse_field([CHECK_DATA])

    def parse_amount(self):
        SUMMA = ['Сумма']
        rects = [self.rects[i + 1] for i, r in enumerate(self.rects) if 'списано' in r.text.lower()]
        rect_opt = rects[0] if rects else None
        res = self._parse_field(SUMMA, default_word_count=2, rectangle=rect_opt)
        if res:
            arr = res.split('Сумма')
            arr_len = len(arr)
            if arr_len == 0:
                parse_res = ''
            elif arr_len == 1:
                parse_res = arr[0]
            else:
                parse_res = ''.join(arr[1:])
            self.amount = ''.join([s for s in parse_res if s.isdigit() or s == '.' or s == ','])
        else:
            self.amount = NOT_DEFINED

    def parse_itogo(self):
        ITOGO = ['Итого']
        res = self._parse_field(ITOGO)
        self.itogo = fix_amount(res)

    def parse_commission(self):
        COMMISSION = 'Комиссия'
        res = self._parse_field([COMMISSION]).replace('О', '0')
        self.commission = ''.join([s for s in res if s.isdigit() or s == '.' or s == ','])

    def parse_document_number(self):
        DOC_NUMBER = ['квитанции']
        self.document_number = self._parse_field(DOC_NUMBER)

    def parse_transaction_number_for_recipient(self):
        TRANSACTION_NUMBER = ['Номер операции']
        self.transaction_number_for_recipient = self._parse_field(TRANSACTION_NUMBER)

    def parse_sbp_id(self):
        SBP = 'Идентификатор операции'
        self.sbp_id = self._parse_field([SBP])

    @property
    def build(self):
        self.parse_sender_card_number()
        self.parse_recipient_card_number()
        self.parse_recipient_phone()
        self.parse_check_date()
        self.parse_amount()
        self.parse_itogo()
        self.parse_commission()
        self.parse_document_number()
        self.parse_transaction_number_for_recipient()
        self.parse_sbp_id()
        return self