from typing import List

from models.data_classes import RectangleData
from utility.comparison.checking_rect import is_rect_belong


def get_sentences(rectangles: List[RectangleData]) -> List[RectangleData]:
    SPACING = 20
    if rectangles:
        rectangles_sorted_y = sorted(rectangles, key=lambda o: o.y)
        lines: List[List[RectangleData]] = []
        line: List[RectangleData] = []
        for r in rectangles_sorted_y:
            low = line[-1].y - line[-1].h / 2 if line else 0
            top = line[-1].y + line[-1].h / 2 if line else 0
            if not line:
                line = [r]
            elif low < r.y < top:
                line.append(r)
            else:
                lines.append(line)
                line = [r]

        if lines and lines[-1] != line:
            lines.append(line)

        res_list = []
        curr_rect: RectangleData = None
        for l in lines:
            if curr_rect:
                res_list.append(curr_rect)
            curr_rect = None
            sorted_line = sorted(l, key=lambda o: o.x)
            count_of_rect = 0
            for r in sorted_line:
                count_of_rect += 1
                if curr_rect is None:
                    curr_rect = r
                elif curr_rect.x + curr_rect.w + SPACING > r.x:
                    new_w = r.x - curr_rect.x + r.w
                    new_text = curr_rect.text + " " + r.text
                    new_y = r.y if r.y < curr_rect.y else curr_rect.y
                    max_y = r.y + r.h if r.y + r.h > curr_rect.y + curr_rect.h else curr_rect.y + curr_rect.h
                    new_h = max_y - new_y #r.h if r.h > curr_rect.h else curr_rect.h
                    curr_rect = RectangleData(x=curr_rect.x, y=new_y, w=new_w, h=new_h, text=new_text)
                else:
                    if curr_rect:
                        res_list.append(curr_rect)
                    curr_rect = r

            if count_of_rect == 1:
                res_list.append(curr_rect)
                curr_rect = None

        res = res_list if res_list else []
        return res
    else:
        []


def get_rect_from_sentences(all_rect: List[RectangleData], sentences: List[RectangleData]) -> List[RectangleData]:
    res = [r for r in all_rect if is_rect_belong(sentences, r)]
    return res


def except_rect_from(all_rect: List[RectangleData], rectangles: List[RectangleData]) -> List[RectangleData]:
    # res = [r for r in all_rect if r not in rectangles]
    res = []
    for ar in all_rect:
        for r in rectangles:
            if ar == r:
                break
        else:
            res.append(ar)
    return res


def get_sentences2(rectangles: List[RectangleData]) -> List[RectangleData]:
    SPACING = 40
    if rectangles:
        rectangles_sorted_y = sorted(rectangles, key=lambda o: o.y)
        lines: List[List[RectangleData]] = []
        line: List[RectangleData] = []
        for r in rectangles_sorted_y:
            low = line[-1].y - line[-1].h  if line else 0
            top = line[-1].y + line[-1].h  if line else 0
            if not line:
                line = [r]
            elif low < r.y < top:
                line.append(r)
            else:
                lines.append(line)
                line = [r]

        if lines and lines[-1] != line:
            lines.append(line)

        res_list = []
        curr_rect: RectangleData = None
        for l in lines:
            if curr_rect:
                res_list.append(curr_rect)
            curr_rect = None
            sorted_line = sorted(l, key=lambda o: o.x)
            count_of_rect = 0
            for r in sorted_line:
                count_of_rect += 1
                if curr_rect is None:
                    curr_rect = r
                elif curr_rect.x + curr_rect.w + SPACING > r.x:
                    new_w = r.x - curr_rect.x + r.w
                    new_text = curr_rect.text + " " + r.text
                    new_y = r.y if r.y < curr_rect.y else curr_rect.y
                    max_y = r.y + r.h if r.y + r.h > curr_rect.y + curr_rect.h else curr_rect.y + curr_rect.h
                    new_h = max_y - new_y #r.h if r.h > curr_rect.h else curr_rect.h
                    curr_rect = RectangleData(x=curr_rect.x, y=new_y, w=new_w, h=new_h, text=new_text)
                else:
                    if curr_rect:
                        res_list.append(curr_rect)
                    curr_rect = r

            if count_of_rect == 1:
                res_list.append(curr_rect)
                curr_rect = None

        res = res_list if res_list else []
        return res
    else:
        []