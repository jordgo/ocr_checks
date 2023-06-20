import base64
from dataclasses import dataclass

import numpy as np
from pydantic import BaseModel, AnyHttpUrl, Field

@dataclass
class RequestBankCheck: #(BaseModel):
    url: str
    img: np.ndarray

    # class Config:
    #     arbitrary_types_allowed = True
