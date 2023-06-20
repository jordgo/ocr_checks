from dataclasses import dataclass, astuple, asdict

import numpy as np


OFFSET_ERROR = 2
e = OFFSET_ERROR


@dataclass(frozen=True)
class TesseractResp:
    text: str
    conf: float
    resize_coeff: int
    frame: np.ndarray

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
