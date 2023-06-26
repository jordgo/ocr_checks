import pytest

from models.data_classes import FrequencyKey
from parsing.post_process import fix_word, create_frequency_dict, create_str_from_frequency_dict, find_words_number, \
    replace_spaces


@pytest.mark.parametrize('text, exp', [
    ('Квитенция № 1-9-131-260-978', 'Квитанция № 1-9-131-260-978'),
    ('Тиньк0фф', 'Тинькофф'),
])
def test_fix_word(text, exp):
    res = fix_word(text)
    assert res == exp


source_arr = [['Квитанция', '—', '№123301641'], ['Квитанция', '—', '№123301641'], ['Квитанция', '—', '№123301641'],
              ['38123301641'], ['862123301641'], ['862123301641'], ['Квитанция', '№123301641'],
              ['Квитанция', '—', '№123301641'], ['Квитанция', '—', '№123301641']]

source_arr1 = [['Квитеанция', '—', '№123301641'], ['Квитанция', '—', '№123301641'], ['Квитанция', '—', '№123301641'],
              ['38123301641'], ['862123301641'], ['862123301641'], ['Квитанция', '№123301641'],
              ['Квитанция', '—', '№123301641'], ['Квитанция', '—', '№123301641']]

# source_arr3

@pytest.mark.parametrize('arr, exp', [
    (source_arr, {FrequencyKey('Квитанция', 0): 6, FrequencyKey('—', 5): 5,
                  FrequencyKey('№123301641', 11): 6, FrequencyKey('38123301641', 0): 1, FrequencyKey('862123301641', 0): 2}),
    (source_arr1, {FrequencyKey('Квитеанция', 0): 1, FrequencyKey('Квитанция', 0): 5, FrequencyKey('—', 5): 5,
                  FrequencyKey('№123301641', 11): 6, FrequencyKey('38123301641', 0): 1,
                  FrequencyKey('862123301641', 0): 2}),
])
def test_create_frequency_dict(arr, exp):
    res = create_frequency_dict(arr)
    assert res == exp


@pytest.mark.parametrize('arr, exp', [
    (source_arr, 'Квитанция — №123301641'),
    (source_arr1, 'Квитанция — №123301641'),
])
def test_create_frequency_dict(arr, exp):
    frequency_dict = create_frequency_dict(arr)
    res = create_str_from_frequency_dict(frequency_dict, arr)
    assert res == exp


@pytest.mark.parametrize('arr, exp', [
    (source_arr, 3),
    ([], 0),
    ([[]], 0),
])
def test_find_words_number(arr, exp):
    res = find_words_number(arr)
    assert res == exp


@pytest.mark.parametrize('arr, exp', [
    (' номер карты получателя', 'номер карты получателя'),
])
def test_replace_spaces(arr, exp):
    res = replace_spaces(arr)
    assert res == exp