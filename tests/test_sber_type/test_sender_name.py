import pytest

from models.types.base_check_type import NOT_DEFINED
from models.data_classes import RectangleData
from models.types.sber_type import SberType


@pytest.mark.parametrize("name, res", [
    ("oleg", "oleg"),
    (None, "oleg"),
])
def test_setter(name, res):
    sber = SberType([])
    # if name is None:
    #     with pytest.raises(TypeError):
    #         sber.sender_name = name
    #     assert sber.sender_name is None #NOT_DEFINED
    # else:
    sber.sender_name = name
    assert sber.sender_name == name


@pytest.mark.parametrize("rects, res", [
    ([RectangleData(1,1,1,1, "some_text"), RectangleData(1,2,1,1, "ФИО отправителя"), RectangleData(1,3,1,1, "Mihail")], "Mihail"),
    ([RectangleData(1,2,1,1, "ФИО отправителя"), RectangleData(1,1,1,1, "some_text"),  RectangleData(1,3,1,1, "Mihail")], "Mihail"),
    ([RectangleData(1, 1, 1, 1, "some_text"), RectangleData(1, 2, 1, 1, ""),RectangleData(1, 3, 1, 1, "Mihail")], NOT_DEFINED),
    ([RectangleData(1, 2, 1, 1, "ФИО отправителя"), RectangleData(1, 1, 1, 1, "some_text")], NOT_DEFINED),
])
def test_parse_sender_name(rects, res):
    sber = SberType(rects)
    sber.parse_sender_name()
    assert res == sber.sender_name


@pytest.mark.parametrize("rects, res", [
    ([RectangleData(1,1,1,1, "some_text"),
      RectangleData(1,2,1,1, "Чек по операции"), RectangleData(1,3,1,1, "05.03.1983"),
      RectangleData(1,4,1,1, "ФИО отправителя"), RectangleData(1,5,1,1, "Mihail"),
      RectangleData(1,6,1,1, "Счет отправителя"), RectangleData(1,7,1,1, "1234"),
      RectangleData(1,8,1,1, "Номер карты получателя"), RectangleData(1,9,1,1, "5678"),
      RectangleData(1,10,1,1, "ФИО получателя"), RectangleData(1,11,1,1, "Oleg"),
      RectangleData(1,12,1,1, "Сумма перевода"), RectangleData(1,13,1,1, "5000"),
      RectangleData(1,14,1,1, "Номер документа"), RectangleData(1,15,1,1, "1111111111111")],
     {'amount': '5000',
      'check_date': '05.03.1983',
      'document_number': '1111111111111',
      'recipient_card_number': '5678',
      'recipient_name': 'Oleg',
      'sender_card_number': '1234',
      'sender_name': 'Mihail'}),
])
def test_build(rects, res):
    sber = SberType(rects).build
    assert res == sber.to_dict



def test_t():
    sber = SberType()
    print('111111111111111111')
    # sber.sender_name = 'tolik'
    print(sber.to_dict)
    assert True

