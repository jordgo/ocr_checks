import pytest

from definition import ROOT_DIR
from main import main
from parsing.post_process import fix_word


# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/sber_1.jpeg", {'sender_name': 'Мурат Дмитриевич Х.', 'sender_card_number': '3714', 'recipient_name': 'Денис Юрьевич К.', 'recipient_card_number': '8124', 'check_date': '6 июня 2023 00:20:12 (МСК)', 'amount': '500,00', 'document_number': '5089428348'}),
#     (ROOT_DIR + "/tests/imgs/sber_2.jpeg", {'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'recipient_name': 'Денис Юрьевич К.', 'recipient_card_number': '8124', 'check_date': '5 июня 2023 15:13:07 (МСК)', 'amount': '320,00 ₽', 'document_number': '4810726820'}),
#     (ROOT_DIR + "/tests/imgs/sber_3.jpeg", {'sender_name': 'Екатерина Фаритовна Е.', 'sender_card_number': '7938', 'recipient_name': 'Алексей Владимирович Х.', 'recipient_card_number': '4558', 'check_date': '6 июня 2023 04:44:21 (МСК)', 'amount': '310,00', 'document_number': '5089792932'}),
#     (ROOT_DIR + "/tests/imgs/sber_4.jpeg", {'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'recipient_name': 'Дмитрий Станиславович И.', 'recipient_card_number': '**** 6662', 'check_date': '6 июня 2023 06:43:39 (МСК)', 'amount': '330,00', 'document_number': '4815759928'}),
#     (ROOT_DIR + "/tests/imgs/sber_5.jpeg", {'sender_name': 'Лариса Святославовна П.', 'sender_card_number': '6436', 'recipient_name': 'Александр Васильевич П.', 'recipient_card_number': '5023', 'check_date': '6 июня 2023 07:08:55 (МСК)', 'amount': '300,00 В', 'document_number': '4627953438'}),
# ])
# def test_full_sber(img_path, exp):
#     res = main(img_path)
#     assert res == exp
#
#
# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/tinkof_1.jpeg", {'sender_name': 'Борис Бородкин', 'recipient_name': 'Алексей Х.', 'recipient_card_number': '+7 (989) 193-75-04', 'check_date': '05.06.2023 02', 'amount': '380 ₽', 'document_number': '1-9-124-261-067'}),
#     (ROOT_DIR + "/tests/imgs/tinkof_2.jpeg", {'sender_name': 'Максим Евсеев', 'recipient_name': 'Александр П.', 'recipient_card_number': '5023', 'check_date': '06.06.2023 08:39:36', 'amount': '500 ₽', 'document_number': '1-9-140-711-867'}),
#     (ROOT_DIR + "/tests/imgs/tinkof_3.jpeg", {'sender_name': 'Кира Гульева', 'recipient_name': 'Александр П.', 'recipient_card_number': '+7 (985) 545-81-45', 'check_date': '05.06.2023 14:24:26', 'amount': '300 ₽', 'document_number': '1-9-131-260-978'}),
# ])
# def test_full_tinkoff(img_path, exp):
#     res = main(img_path)
#     assert res == exp
#
#
# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/qiwi_1.jpeg", {'transaction_number_for_recipient': '1686030173562', 'sender_card_number': '79146519030', 'recipient_card_number': '8124', 'check_date': '06.06.2023 в 08:42 (МСК)', 'amount': '407 Р', 'document_number': '27597008748'}),
# ])
# def test_full_qiwi(img_path, exp):
#     res = main(img_path)
#     assert res == exp
#
#
# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/raif_1.jpeg", {'recipient_phone': '79891937504', 'recipient_name': 'Алехсей Владимирович Х', 'sender_name': 'Моисеенко Сандра Александровна', 'sender_card_number': '40817810701101911867', 'check_date': '06 июн 2025 03:13:00', 'amount': '440', 'document_number': 'N1 06 июн. 2023 03:13:45'}),
# ])
# def test_full_raif(img_path, exp):
#     res = main(img_path)
#     assert res == exp
#
#
# # @pytest.mark.parametrize('img_path, exp', [
# #     (ROOT_DIR + "/tests/imgs/alfa_1.jpeg",),
# # ])
# # def test_full_alfa(img_path, exp):
# #     res = main(img_path)
# #     assert res == exp
#
#
# @pytest.mark.parametrize('img_path, exp', [
#     (ROOT_DIR + "/tests/imgs/vtb_1.jpeg", {'recipient_phone': '+7(989)193-61-01', 'recipient_name': 'Александр Сергеевич Б', 'sender_card_number': '*5267', 'sender_name': 'Олег Алексеевич М.', 'check_date': '05.06.2023, 19:44', 'amount': '500 ₽', 'document_number': 'А31561644508452400070011000503'}),
# ])
# def test_full_vtb(img_path, exp):
#     res = main(img_path)
#     assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/sber/sber_1.jpeg", {'recipient_card_number': '8124', 'recipient_name': 'Денис Юрьевич К.', 'sender_name': 'Мурат Дмитриевич Х.', 'sender_card_number': '3714', 'check_date': '6 июня 2023 00:20:12 (МСК)', 'amount': '500,00', 'document_number': '5089428348'}),
    (ROOT_DIR + "/tests/imgs/sber/sber_2.jpeg", {'recipient_card_number': '8124', 'recipient_name': 'Денис Юрьевич К.', 'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'check_date': '5 июня 2023 15:13:07 (МСК)', 'amount': '320,00', 'document_number': '4810726820'}),
    (ROOT_DIR + "/tests/imgs/sber/sber_3.jpeg", {'document_number': '5089792932', 'recipient_card_number': '4558', 'recipient_name': 'Апексей Владимирович Х.', 'sender_name': 'Екатерина Фаритовна Е.', 'sender_card_number': '7938', 'check_date': '6 июня 2023 04:44:21 (МСК)', 'amount': '310,00'}),
    (ROOT_DIR + "/tests/imgs/sber/sber_4.jpeg", {'document_number': '4815759928', 'recipient_card_number': '6662', 'recipient_name': 'Дмитрий Станиславович И.', 'sender_name': 'Юрий Александрович Л.', 'sender_card_number': '7306', 'check_date': '6 июня 2023 06:43:39 (МСК)', 'amount': '330,00'}),
    (ROOT_DIR + "/tests/imgs/sber/sber_5.jpeg", {'document_number': '4627953438', 'recipient_card_number': '5023', 'recipient_name': 'Александр Васильевич П.', 'sender_name': 'Лариса Святославовна П.', 'sender_card_number': '6436', 'check_date': '6 июня 2023 07:08:55 (МСК)', 'amount': '300,00'}),
])
def test_full_sber(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/tinkof/tinkof_1.jpeg", {'recipient_card_number': '+7 (989) 193-75-04', 'recipient_name': 'Алексей Х.', 'sender_name': 'Борис Бородкин', 'check_date': '05.06.2023 02:33:24', 'amount': '380', 'document_number': '1-9-124-261-067'}),
    (ROOT_DIR + "/tests/imgs/tinkof/tinkof_2.jpeg", {'document_number': '1-9-140-711-867', 'recipient_card_number': '220220******5023', 'recipient_name': 'Александр П.', 'sender_name': 'Максим Евсеев', 'check_date': '06.06.2023 08:39:36', 'amount': '500'}),
    (ROOT_DIR + "/tests/imgs/tinkof/tinkof_3.jpeg", {'recipient_card_number': '+7 (985) 545-81-45', 'recipient_name': 'Александр П.', 'sender_name': 'Кира Гульева', 'check_date': '05.06.2023 14:24:26', 'amount': '300', 'document_number': '1-9-131-260-978'}),
])
def test_full_tinkoff(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/qiwi/qiwi_1.jpeg", {'document_number': '27597008748', 'recipient_card_number': '8124', 'transaction_number_for_recipient': '1686030173562', 'sender_card_number': '79146519030', 'check_date': '06.06.2023 в 08:42 (МСК)', 'amount': '407'}),
])
def test_full_qiwi(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/raif/raif_1.jpeg", {'document_number': 'N1 06 июн. 2023 03:13:45', 'recipient_phone': '79891937504', 'recipient_name': 'Алексей Владимирович Х', 'sender_name': 'Моисеенко Сандра Александровна', 'sender_card_number': '40817810701101911867', 'check_date': '06 июн 2025 03:13:00', 'amount': '440'}),
])
def test_full_raif(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/alfa/alfa_2.png", {'sbp_id': 'АЗ170201516025010000080011010304', 'sender_card_number': '40817810105850401301', 'recipient_phone': '79891937545', 'recipient_name': 'Денис Юрьевич К', 'check_date': '19.06.2023 23:15:15', 'amount': '1800.00.'}),
])
def test_full_alfa(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/vtb/vtb_1.jpeg", {'sbp_id': 'АЗ156164450845240000070011000503', 'recipient_phone': '+7(989)193-61-01', 'recipient_name': 'Александр Сергеевич Б', 'sender_card_number': '5267', 'sender_name': 'Олег Алексеевич М.', 'check_date': '05.06.2023, 19:44', 'amount': '500'}),
])
def test_full_vtb(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/ros/ros_1.png", {'sbp_id': '9328470059 40817810746003255321', 'recipient_card_number': '5321', 'recipient_phone': '+79328470059', 'recipient_name': 'Идель Ишбулатович Р.', 'sender_card_number': '2582', 'sender_name': 'Антонов Валентин Александрович', 'check_date': '20.06.2023 15:05', 'amount': '1500.00'}),
])
def test_full_ros(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/ural/ural_1.jpg", {'sbp_id': 'А31691227154320Р0000070011010304', 'recipient_phone': '+7 (989) 193-61-02', 'recipient_name': 'Дмитрий Станиславович И.', 'sender_name': 'БЛАХОВА ТАТЬЯНА ШИХАМОВНА', 'check_date': '18.06.2023 15:27', 'amount': '500.00', 'document_number': '123301641'}),
])
def test_full_ural(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/ural/ural_1.jpg", {'sbp_id': 'А31691227154320Р0000070011010304', 'recipient_phone': '+7 (989) 193-61-02', 'recipient_name': 'Дмитрий Станиславович И.', 'sender_name': 'БЛАХОВА ТАТЬЯНА ШИХАМОВНА', 'check_date': '18.06.2023 15:27', 'amount': '500.00', 'document_number': '123301641'}),
])
def test_full_ural(img_path, exp):
    res = main(img_path)
    assert res == exp


@pytest.mark.parametrize('img_path, exp', [
    (ROOT_DIR + "/tests/imgs/sov/sov_2.png", {'document_number': 'М45595373041', 'recipient_card_number': '8579', 'sender_card_number': '4020', 'check_date': '20.06.2023, 12:08', 'amount': '1000'}),
])
def test_full_ural(img_path, exp):
    res = main(img_path)
    assert res == exp