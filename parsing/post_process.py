

words = {
    'Ленис': 'Денис',
    'Квитенция': 'Квитанция',
    'тиньк0фф': 'Тинькофф',
    'тинькофо': 'Тинькофф',
    'тиньк0фо': 'Тинькофф',
}


def fix_word(text: str) -> str:
    for w in words:
        if w in text:
            text = text.replace(w, words[w])

        if w.replace(' ', '').lower() == text.replace(' ', '').lower():
            text = words[w]
    return text
