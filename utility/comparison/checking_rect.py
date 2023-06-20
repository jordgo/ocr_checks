from typing import List

from models.data_classes import RectangleData


def is_rect_belong(source_rect: List[RectangleData], rect: RectangleData) -> bool:
    if not source_rect:
        return False

    for st_rect in source_rect:
        if rect in st_rect:
            return True

    return False


def is_list_contains_rect(rect_list: List[RectangleData], rect: RectangleData) -> bool:
    if not rect_list:
        return False

    for st_rect in rect_list:
        if rect == st_rect:
            return True

    return False


def is_list_contains_rect_text(rect_list: List[RectangleData], rect: RectangleData) -> bool:
    if not rect_list:
        return False

    for st_rect in rect_list:
        st_rect_text = st_rect.text.replace(" ", "").lower()
        rect_text = rect.text.replace(" ", "").lower()
        if st_rect_text == rect_text:
            return True

    return False
