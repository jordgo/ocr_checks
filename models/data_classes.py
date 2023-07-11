from dataclasses import dataclass, astuple, asdict
from typing import List

import numpy as np


OFFSET_ERROR = 2
e = OFFSET_ERROR


@dataclass(frozen=True)
class TesseractResp:
    text: str
    conf: float
    resize_coeff: int
    frame: np.ndarray
    results: List[str]

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class RectangleData:
    x: int
    y: int
    w: int
    h: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)

    def __iter__(self):
        return iter(astuple(self))

    def __contains__(self, rectangle_data) -> bool:
        ix, iy, iw, ih, _ = rectangle_data
        return ix >= self.x and \
            iy >= self.y and \
            iw <= self.w and \
            ih <= self.h and \
            ix + iw <= self.x + self.w and \
            iy + ih <= self.y + self.h
    
    def __eq__(self, other) -> bool:
        res = self.x - e < other.x < self.x + e and \
                self.y - e < other.y < self.y + e and \
                self.w - e < other.w < self.w + e and \
                self.h - e < other.h < self.h + e
        return res

    def __hash__(self):
        return hash((self.x, self.y))

    @staticmethod
    def empty():
        return RectangleData(0, 0, 0, 0, '')


@dataclass
class FrequencyKey:
    value: str
    order:  int
    count: int = 1

    def __hash__(self):
        return hash((self.value))

    def increment_order(self, new_order):
        self.order += new_order
        self.count += 1

    @property
    def avg_order(self) -> float:
        return self.order / self.count if self.count != 0 else 0