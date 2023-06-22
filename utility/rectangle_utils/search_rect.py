from typing import List, Optional

from models.data_classes import RectangleData


def find_rect_opt(rects: List[RectangleData], value: str) -> Optional[RectangleData]:
    results: List[RectangleData] = [r for r in rects if value in r.text]
    if results:
        return results[0]
    else:
        return None
