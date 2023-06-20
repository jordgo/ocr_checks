import pytest

from parsing.post_process import fix_word


@pytest.mark.parametrize('text, exp', [
    ('Квитенция № 1-9-131-260-978', 'Квитанция № 1-9-131-260-978'),
    ('Тиньк0фф', 'Тинькофф'),
])
def test_fix_word(text, exp):
    res = fix_word(text)
    assert res == exp
