import pytest

from definition import ROOT_DIR
from main import main
from parsing.post_process import fix_word


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/sber_1.jpeg", {'sender_name': 'Мурат Дмитриевич Х.', 'sender_card_number': '3714', 'recipient_name': 'Денис Юрьевич К.', 'recipient_card_number': '8124', 'check_date': '6 июня 2023 00:20:12 (МСК)', 'amount': '500,00', 'document_number': '5089428348'}),
    (ROOT_DIR + "/tests/imgs/sber_2.jpeg", {'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'recipient_name': 'Денис Юрьевич К.', 'recipient_card_number': '8124', 'check_date': '5 июня 2023 15:13:07 (МСК)', 'amount': '320,00 ₽', 'document_number': '4810726820'}),
    (ROOT_DIR + "/tests/imgs/sber_3.jpeg", {'sender_name': 'Екатерина Фаритовна Е.', 'sender_card_number': '7938', 'recipient_name': 'Алексей Владимирович Х.', 'recipient_card_number': '4558', 'check_date': '6 июня 2023 04:44:21 (МСК)', 'amount': '310,00', 'document_number': '5089792932'}),
    (ROOT_DIR + "/tests/imgs/sber_4.jpeg", {'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'recipient_name': 'Дмитрий Станиславович И.', 'recipient_card_number': '**** 6662', 'check_date': '6 июня 2023 06:43:39 (МСК)', 'amount': '330,00', 'document_number': '4815759928'}),
    (ROOT_DIR + "/tests/imgs/sber_5.jpeg", {'sender_name': 'Лариса Святославовна П.', 'sender_card_number': '6436', 'recipient_name': 'Александр Васильевич П.', 'recipient_card_number': '5023', 'check_date': '6 июня 2023 07:08:55 (МСК)', 'amount': '300,00 В', 'document_number': '4627953438'}),
])
def test_full_sber(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/tinkof_1.jpeg", {'sender_name': 'Борис Бородкин', 'recipient_name': 'Алексей Х.', 'recipient_card_number': '+7 (989) 193-75-04', 'check_date': '05.06.2023 02', 'amount': '380 ₽', 'document_number': '1-9-124-261-067'}),
    (ROOT_DIR + "/tests/imgs/tinkof_2.jpeg", {'sender_name': 'Максим Евсеев', 'recipient_name': 'Александр П.', 'recipient_card_number': '5023', 'check_date': '06.06.2023 08:39:36', 'amount': '500 ₽', 'document_number': '1-9-140-711-867'}),
    (ROOT_DIR + "/tests/imgs/tinkof_3.jpeg", {'sender_name': 'Кира Гульева', 'recipient_name': 'Александр П.', 'recipient_card_number': '+7 (985) 545-81-45', 'check_date': '05.06.2023 14:24:26', 'amount': '300 ₽', 'document_number': '1-9-131-260-978'}),
])
def test_full_tinkoff(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/qiwi_1.jpeg", {'transaction_number_for_recipient': '1686030173562', 'sender_card_number': '79146519030', 'recipient_card_number': '8124', 'check_date': '06.06.2023 в 08:42 (МСК)', 'amount': '407 Р', 'document_number': '27597008748'}),
])
def test_full_qiwi(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/raif_k1.jpeg", {'recipient_phone': '79891937504', 'recipient_name': 'Алехсей Владимирович Х', 'sender_name': 'Моисеенко Сандра Александровна', 'sender_card_number': '40817810701101911867', 'check_date': '06 июн 2025 03:13:00', 'amount': '440', 'document_number': 'N1 06 июн. 2023 03:13:45'}),
])
def test_full_raif(img_path, exp):
    res = main(img_path)
    assert res == exp


# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/sbp_1_alfa.jpeg",),
# ])
# def test_full_alfa(img_path, exp):
#     res = main(img_path)
#     assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/vtb_1.jpeg", {'recipient_phone': '+7(989)193-61-01', 'recipient_name': 'Александр Сергеевич Б', 'sender_card_number': '*5267', 'sender_name': 'Олег Алексеевич М.', 'check_date': '05.06.2023, 19:44', 'amount': '500 ₽', 'document_number': 'А31561644508452400070011000503'}),
])
def test_full_vtb(img_path, exp):
    res = main(img_path)
    assert res == exp