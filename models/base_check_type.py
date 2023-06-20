import abc
import dataclasses
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

from models.data_classes import RectangleData


_logger = logging.getLogger("app")


NOT_DEFINED = 'not defined'


@dataclass
class BaseCheckType(abc.ABC):
    sender_name: str = None
    sender_card_number: str = None
    recipient_name: str = None
    recipient_card_number: str = None
    check_date: str = None
    amount: str = None
    document_number: str = None
    @abc.abstractmethod
    def parse_sender_name(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_sender_card_number(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_recipient_name(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_recipient_card_number(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_check_date(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_amount(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_document_number(self):
        return NotImplemented

    @staticmethod
    @abc.abstractmethod
    def create(rects: List[RectangleData]):
        return NotImplemented

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

    @property
    def to_dict(self):
        return dataclasses.asdict(self)

    @property
    def to_json(self):
        return json.dumps(self.to_dict,
                          ensure_ascii=False,
                          separators=(',', ':')
                          )


# class TinkofType(BaseCheckType):
#     pass
#
#
# class VTBType(BaseCheckType):
#     pass
#
#
# class RaifType(BaseCheckType):
#     pass
#
#
# class QiwiType(BaseCheckType):
#     pass
#
#
# class SbpType(BaseCheckType):
#     pass


