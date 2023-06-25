import numpy as np

from models.types.alfa_sbp_type import AlfaSbpType
from models.types.base_check_type import BaseCheckType
from models.data_classes import RectangleData
from models.types.qiwi_type import QiwiType
from models.types.raiffaizen_type import RaiffaizenType
from models.types.ros_type import RosType
from models.types.sber_type import SberType
from models.types.sov_type import SovType
from models.types.tinkof_type import TinkoffType
from models.types.ural_type import UralType
from models.types.vtb_type import VTBType

all_creators = [SberType.create,
                TinkoffType.create,
                QiwiType.create,
                RaiffaizenType.create,
                AlfaSbpType.create,
                VTBType.create,
                RosType.create,
                UralType.create,
                SovType.create
                ]


def find_type(rects: [RectangleData], img: np.ndarray) -> BaseCheckType:
    for creator in all_creators:
        res = creator(rects, img)
        if res:
            return res
    raise TypeError("Type Not Found")