

words = {
    'Ленис': 'Денис',
    'Квитенция': 'Квитанция',
    'тиньк0фф': 'Тинькофф',
    'тинькофо': 'Тинькофф',
    'тиньк0фо': 'Тинькофф',
    'Плательшик': 'Плательщик',
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