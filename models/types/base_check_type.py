import abc
import dataclasses
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np

from models.data_classes import RectangleData


_logger = logging.getLogger("app")


NOT_DEFINED = 'not defined'


@dataclass
class BaseCheckType(abc.ABC):
    check_date: str = None
    amount: str = None

    @abc.abstractmethod
    def parse_check_date(self):
        return NotImplemented

    @abc.abstractmethod
    def parse_amount(self):
        return NotImplemented

    @staticmethod
    @abc.abstractmethod
    def create(rects: List[RectangleData], img: np.ndarray):
        return NotImplemented

    @abc.abstractmethod
    def build(self):
        return NotImplemented

    @property
    def to_dict(self):
        return dataclasses.asdict(self)

    @property
    def to_json(self):
        return json.dumps(self.to_dict,
                          ensure_ascii=False,
                          separators=(',', ':')
                          )

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


