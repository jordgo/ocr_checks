import numpy as np

from models.types.alfa_sbp_type import AlfaSbpType
from models.types.base_check_type import BaseCheckType
from models.data_classes import RectangleData
from models.types.qiwi_type import QiwiType
from models.types.raiffaizen_type import RaiffaizenType
from models.types.sber_type import SberType
from models.types.tinkof_type import TinkoffType
from models.types.vtb_type import VTBType

all_creators = [SberType.create,
                TinkoffType.create,
                QiwiType.create,
                RaiffaizenType.create,
                AlfaSbpType.create,
                VTBType.create,
                ]


def find_type(rects: [RectangleData], img: np.ndarray) -> BaseCheckType:
    for creator in all_creators:
        res = creator(rects, img)
        if res:
            return res
    raise TypeError("Type Not Found")