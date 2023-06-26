import logging
from typing import Callable, List, Dict

from models.data_classes import RectangleData, FrequencyKey
from models.types.base_check_type import NOT_DEFINED


_logger = logging.getLogger("app")


words = {
    'Ленис': 'Денис',
    'Квитенция': 'Квитанция',
    'тиньк0фф': 'Тинькофф',
    'тинькофо': 'Тинькофф',
    'тиньк0фо': 'Тинькофф',
    'лательшик': 'лательщик',
    'Запеление': 'Заявление',
    'Запаление': 'Заявление',
    'Счёт': 'Счет',
    'счёт': 'счет',
    'Телефсн': 'Телефон',
}


def fix_word(text: str) -> str:
    for w in words:
        if w in text:
            text = text.replace(w, words[w])

        if replace_spaces(w).lower() == replace_spaces(text).lower():
            text = words[w]
    return text


def replace_spaces(raw_str: str) -> str:
    for i in range(4):
        raw_str = raw_str.replace('  ', ' ')
    return raw_str.strip()


def fix_amount(raw_str: str) -> str:
    if len(raw_str) > 1:
        maaybe_sum = raw_str.split(' ')[0]
        return ''.join([s for s in maaybe_sum if s.isdigit() or s == '.' or s == ','])
    else:
        return NOT_DEFINED


def clear_card_number(raw_str: str) -> str:
    return ''.join([s for s in raw_str if s.isdigit()]) #s.replace('*', '').replace(' ', '').strip()


def extract_last(raw_str: str) -> str:
    str_origin = replace_spaces(raw_str)
    arr = str_origin.split(' ')
    if len(arr) > 1:
        res_arr = arr[-1]
    else:
        res_arr = [NOT_DEFINED]
    return ''.join(res_arr)


def extract_last_numbers(number_excluded: int) -> Callable:
    def body(raw_str: str) -> str:
        str_origin = replace_spaces(raw_str)
        arr = str_origin.split(' ')
        if len(arr) > number_excluded:
            res_arr = arr[-number_excluded:]
        else:
            res_arr = [NOT_DEFINED]
        return ' '.join(res_arr)
    return body


def extract_except_from_start(number_excluded: int) -> Callable:
    def body(raw_str: str) -> str:
        str_origin = replace_spaces(raw_str)
        arr = str_origin.split(' ')
        if len(arr) > number_excluded:
            res_arr = arr[number_excluded:]
        else:
            res_arr = [NOT_DEFINED]
        return ' '.join(res_arr)
    return body


def neighboring_rect(rects: List[RectangleData], curr_rect: RectangleData, i: int):
    h = curr_rect.h / 2
    prev_rect = rects[i - 1]
    if curr_rect.y - h < prev_rect.y < curr_rect.y + h:
        return rects[i - 1]

    next_rect = rects[i + 1]
    if curr_rect.y - h < next_rect.y < curr_rect.y + h:
        return rects[i + 1]


def create_frequency_dict(arr: List[List[str]]) -> Dict[FrequencyKey, int]:
    _logger.info(f"Source Frequency Dict {arr}")
    frequency_dict: Dict[FrequencyKey, int] = {}
    if arr:
        for arr_words in arr:
            for count, word in enumerate(arr_words):
                for fd_key in frequency_dict:
                    if word == fd_key.value:
                        fd_key.increment_order(count)
                        frequency_dict[fd_key] += 1
                        break
                else:
                    frequency_dict[FrequencyKey(word, count)] = 1
    frequency_dict_sort = {k: v for k, v in sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True)}
    _logger.info(f"Frequency DictSorted {frequency_dict_sort}")
    # frequency_dict_filtered = {}
    # for d in frequency_dict_sort:
    #     keys = frequency_dict_filtered.keys()
    #     orders: List[int] = [k.order for k in keys]
    #     if len(frequency_dict_filtered) == 0:
    #         frequency_dict_filtered[d] = frequency_dict_sort[d]
    #     elif d.order not in orders:
    #         frequency_dict_filtered[d] = frequency_dict_sort[d]
    #     else:
    #         continue
    # _logger.info(f"Frequency DictFiltered {frequency_dict_filtered}")
    return frequency_dict_sort


def create_str_from_frequency_dict(f_dict: Dict[FrequencyKey, int], arr: List[List[str]]) -> str:
    result_arr: List[FrequencyKey] = []
    if arr and arr[0]:
        max_len = find_words_number(arr)
        for f_key, n in f_dict.items():
            if n > 2 and len(result_arr) < max_len:
                result_arr.append(f_key)
    sorted_res_arr = sorted(result_arr, key=lambda k: k.avg_order)
    result_text = ' '.join([a.value for a in sorted_res_arr])
    _logger.info(f"Result Text: <{result_text}")
    return result_text


def find_words_number(arr: List[List[str]]) -> int:
    frequency_dict = {}
    if arr:
        for arr_words in arr:
            arr_len = len(arr_words)
            for fd_key in frequency_dict:
                if arr_len == fd_key:
                    frequency_dict[arr_len] += 1
                    break
            else:
                frequency_dict[arr_len] = 1
    _logger.info(f"Frequency of arr len <{frequency_dict}>")
    if frequency_dict:
        res = sorted(frequency_dict.items(), key=lambda v: v[1], reverse=True)[0][0]
        _logger.info(f"Number of words {res}")
        return res
    else:
        _logger.warning(f"Dict is empty, Number of words <{0}>")
        return 0


def extract_digits(raw_str: str) -> str:
    return ''.join([s for s in replace_spaces(raw_str) if s.isdigit()])

