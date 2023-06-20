import pytest

from definition import ROOT_DIR
from main import main
from parsing.post_process import fix_word


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/sber_1.jpeg", {'sender_name': 'Мурат Дмитриевич Х.', 'sender_card_number': '3714', 'recipient_name': 'Денис Юрьевич К.', 'recipient_card_number': '8124', 'check_date': '6 июня 2023 00:20:12 (МСК)', 'amount': '500,00', 'document_number': '5089428348'}),
    # ('Тиньк0фф', 'Тинькофф'),
])
def test_full(img_path, exp):
    res = main(img_path)
    assert res == exp