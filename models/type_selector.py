from typing import List

from models.base_check_type import BaseCheckType
from models.data_classes import RectangleData
from models.sber_type import SberType
from models.tinkof_type import TinkoffType

all_creators = [SberType.create, TinkoffType.create]


def find_type(rects: [RectangleData]) -> BaseCheckType:
    for creator in all_creators:
        res = creator(rects)
        if res:
            return res
    raise TypeError("Type Not Found")