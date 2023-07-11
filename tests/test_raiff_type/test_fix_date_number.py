import pytest

from models.types.raiffaizen_type import _fix_time, _cut_from_first_digit, _extract_number, extract_except_from_start, \
    replace_spaces, extract_last


@pytest.mark.parametrize('raw_str, exp', [
    ('031345', '03:13:45'),
    ('03:1345', '03:13:45'),
    ('0313:45', '03:13:45'),
    ('03:13:45', '03:13:45'),
    ('0313:4', '03134'),
    (' ', ' '),
])
def test_fix_time(raw_str, exp):
    res = _fix_time(raw_str)
    assert res == exp


@pytest.mark.parametrize('raw_str, exp', [
    ('Заявление на рублевый п М1 06 июн. 2023 031345', 'N1 06 июн. 2023 03:13:45'),
    ('Заявление на рублевый п М 1 06 июн. 2023 03:1345', 'N1 06 июн. 2023 03:13:45'),
    (' ', None),
    ('№1 06 2023 031345', None)
])
def test_fix_time(raw_str, exp):
    res = _extract_number(raw_str)
    assert res == exp


@pytest.mark.parametrize('raw_str, exp', [
    ('Заявление на рублевый п М1 06 июн. 2023 031345', '1 06 июн. 2023 031345'),
    (' ', ' '),
])
def test_cut_from_first_digit(raw_str, exp):
    res = _cut_from_first_digit(raw_str)
    assert res == exp


@pytest.mark.parametrize('raw_str, number_excluded, exp', [
    ('Заявление на рублевый п М1 06 июн. 2023 031345', 1, 'на рублевый п М1 06 июн. 2023 031345'),
    ('Заявление    на    рублевый п М1 06 июн. 2023 031345', 3, 'п М1 06 июн. 2023 031345'),
    ('Заявление на рублевый п М1 06 июн. 2023 031345', 2, 'рублевый п М1 06 июн. 2023 031345'),
    ('Заявление    на    рублевый п М1 06 июн. 2023 031345', 4, 'М1 06 июн. 2023 031345'),
    ('Заявление    на    рублевый п М1 06 июн. 2023 031345', 40, None),
    (' ', 1, None),
])
def test_extract_except_first(raw_str, number_excluded, exp):
    res = extract_except_from_start(number_excluded)(raw_str)
    assert res == exp


@pytest.mark.parametrize('raw_str, exp', [
    ('   Заявление       на    рублевый п    М1   ', 'Заявление на рублевый п М1'),
])
def test_replace_spaces(raw_str, exp):
    res = replace_spaces(raw_str)
    assert res == exp


@pytest.mark.parametrize('raw_str, exp', [
    ('Заявление на рублевый п М1 06 июн. 2023 031345', '031345'),
    (' Заявление    на    рублевый п М1 06 июн. 2023 031345  ', '031345'),
    (' ', None),
])
def test_extract_last(raw_str, exp):
    res = extract_last(raw_str)
    assert res == exp