from Crypto.Util.strxor import strxor_c


LETTER_MAP = {
    ' ': 18.74,
    'E': 9.60,
    'T': 7.02,
    'A': 6.21,
    'O': 5.84,
    'I': 5.22,
    'N': 5.21,
    'H': 4.87,
    'S': 4.77,
    'R': 4.43,
    'D': 3.52,
    'L': 3.20,
    'U': 2.25,
    'M': 1.94,
    'C': 1.88,
    'W': 1.82,
    'G': 1.66,
    'F': 1.62,
    'Y': 1.56,
    'P': 1.31,
    ',': 1.24,
    '.': 1.21,
    'B': 1.19,
    'K': 0.74,
    'V': 0.71,
    '"': 0.67,
    '\'': 0.44,
    '-': 0.26,
    '?': 0.12,
    'X': 0.12,
    'J': 0.12,
    ';': 0.08,
    '!': 0.08,
    'Q': 0.07,
    'Z': 0.07,
    ':': 0.03,
    '1': 0.02,
    '0': 0.01,
    ')': 0.01,
    '*': 0.01,
    '(': 0.01,
    '2': 0.01,
    '`': 0.01,
    '3': 0.01,
    '9': 0.01,
    '5': 0.01,
    '4': 0.01,
    '8': 0.00,
    '7': 0.00,
    '6': 0.00,
    '/': 0.00,
    '_': 0.00,
    '[': 0.00,
    '»': 0.00,
    ']': 0.00,
    '«': 0.00,
    '=': 0.00,
    '´': 0.00,
    '>': 0.00,
    '~': 0.00,
    '<': 0.00,
    '#': 0.00,
    '·': 0.00,
    '&': 0.00,
    '{': 0.00,
    '}': 0.00,
    '^': 0.00,
    '|': 0.00,
    '\\': 0.00,
    '@': 0.00,
    '%': 0.00,
    '$': 0.00,
    'Ñ': 0.00
}


def calculate_deviation(message):
    result = 0.0
    message = message.upper()
    #print("chekcing " + binascii.unhexlify(message).decode())

    # Loop over all chars and check their frequency in the message
    for letter, frequency in LETTER_MAP.items():
        count_in_message = message.count(ord(letter))

        frequency_in_message = float(count_in_message) / len(message) * 100.0

        # The difference between statistical and measured frequency should be 0 ideally
        # In the worst case it completely differs
        deviation = abs(frequency_in_message - frequency)
        result += deviation
        #print("There are %d %c's in the message, that is %.f%% compared to expected %.2f%%, deviation = %f" % (count_in_message, letter, frequency_in_message, frequency, deviation))

    return result


def count_english_words(message, wordlist):
    assert type(message) == bytes

    result = 0

    try:
        words = message.decode().lower().split(' ')
        for word in words:
            result += 1 if wordlist.find(word) != -1 else -1
    except UnicodeDecodeError:
        pass

    return result


def calculate_score(s):
    score = 0
    for i in s:
        c = chr(i).upper()
        if c in LETTER_MAP:
            score += LETTER_MAP[c]
    return score


def break_single_byte_xor(bytes_data, mode='score'):

    candidates = [(key, strxor_c(bytes_data, key)) for key in range(256)]

    if mode == 'score':
        return max(candidates, key=lambda x: calculate_score(x[1]))
    elif mode == 'deviation':
        return min(candidates, key=lambda x: calculate_deviation(x[1]))
    elif mode == 'words':
        with open('/usr/share/dict/american-english') as file:
            wordlist = file.read()
        return max(candidates, key=lambda x: count_english_words(x[1], wordlist))



