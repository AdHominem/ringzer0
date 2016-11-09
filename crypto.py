from Crypto.Util.strxor import strxor_c
from binascii import *
from functools import *
import itertools

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


def caesar_cipher(string, key):
    assert type(string) == str and type(key) == int

    return ''.join([chr((ord(c) + key - ord('A')) % 26 + ord('A')) if c.isupper()
                    else chr((ord(c) + key - ord('a')) % 26 + ord('a')) if c.islower()
                    else c for c in string])





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


# Dismisses any string containing non printable chars and gives all valid strings a score
# based on the frequency of the chars
def calculate_score(s):
    score = 0
    for byte in s:
        c = chr(byte).upper()
        if c in LETTER_MAP:
            score += LETTER_MAP[c]
        else:
            return 0
    return score


def break_caesar_cipher(string):
    assert type(string) == str

    return [caesar_cipher(string, key) for key in range(26)]


# Determines the quality of a candidate by using the majority of score, deviation and words
# Words will be the fallback in case all are different
def break_single_byte_xor(bytes_data):

    candidates = [(key, strxor_c(bytes_data, key)) for key in range(256)]
    # overview = [(candidate, calculate_deviation(candidate[1])) for candidate in candidates]
    # for c, s in overview:
    #     if s < 150:
    #         print(c, s)

    score = max(candidates, key=lambda x: calculate_score(x[1]))
    return score
    # deviation = min(candidates, key=lambda x: calculate_deviation(x[1]))
    # if score == deviation:
    #     return score
    #
    # with open('/usr/share/dict/american-english') as file:
    #     wordlist = file.read()
    # words = max(candidates, key=lambda candidate: count_english_words(candidate[1], wordlist))
    #
    # return words


def multi_byte_xor(bytes_data, bytes_key):
    assert len(bytes_data) > len(bytes_key)

    result = bytearray()
    for i in range(len(bytes_data)):
        result.append(bytes_data[i] ^ bytes_key[i % len(bytes_key)])

    return bytes(result)


def break_multi_byte_xor(bytes_data):
    print("Breaking", hexlify(bytes_data)),

    best_keysize_and_distance = (None, 8)

    # 1. Hamming distance: Try all keysizes up until either 40
    for keysize in range(2, min(len(bytes_data) // 3, 40) + 1):

        chunks = [bytes_data[j: j + keysize] for j in [i * keysize for i in range(len(bytes_data) // keysize)]]
        normalized_hamming_distance = get_normalized_hamming_distance(bytes_data, keysize)#hamming_distance(chunks[:2]) / keysize

        if normalized_hamming_distance < best_keysize_and_distance[1]:
            best_keysize_and_distance = (keysize, normalized_hamming_distance)

    keysize = best_keysize_and_distance[0]
    print("Keysize is probably", keysize)

    # 2. Split the data in chunks of keysize
    # If the byte length of the data is not divisible by keysize, this will omit up to keysize - 1 trailing bytes
    chunks = [bytes_data[j: j + keysize] for j in [i * keysize for i in range(len(bytes_data) // keysize)]]
    print("Chunks:", [hexlify(i) for i in chunks])

    # 3. Transpose blocks: Take the i-th elements of each chunk and join them as a new byte block which is encrypted
    # with the same byte
    blocks = [b''.join([bytes([chunk[i]]) for chunk in chunks]) for i in range(keysize)]
    print("Blocks:", [hexlify(block) for block in blocks])

    # 4. Break the individual blocks and assemble the key
    key = b''.join([bytes([break_single_byte_xor(block)[0]]) for block in blocks])
    print("The key is", key, "and the decrypted message is", multi_byte_xor(bytes_data, key))


def hamming_distance(bytes_data):
    #print([hexlify(byte) for byte in bytes_data])

    result = 0
    data_as_integers = [int.from_bytes(byte, byteorder='big') for byte in bytes_data]
    distance = reduce(lambda x, y: x ^ y, data_as_integers)
    while distance > 0:
        result += distance % 2
        #print("Distance:", hex(distance), "Bit:", distance % 2)
        distance >>= 1
    return result


def get_hamming_distance(s1, s2):
    distance = 0
    for c1, c2 in zip(s1, s2):
        for i in range(8):
            if (c1 & 1 << i) != (c2 & 1 << i):
                distance += 1

    return distance


def get_normalized_hamming_distance(s, keysize, n=2):
    slices = [s[keysize*i:keysize*(i+1)] for i in range(n)]
    pairs = list(itertools.combinations(slices, 2))
    dist = float(sum([get_hamming_distance(pair[0], pair[1]) for pair in pairs]))/float(len(pairs))
    return float(dist) / float(keysize)

# message = b'This is a secret message, it is pretty long and hopefully you can decode it'
# message2 = b'Probably too short'
# message3 = b'This is a secret message, pretty short'
# key = b'10'
# cipher = multi_byte_xor(message2, key)
# break_multi_byte_xor(cipher)

# first = b'\x00\xff\x88'     # 0000 0000  1111 1111  1000 1000
# second = b'\x01\xfe\x87'    # 0000 0001  1111 1110  1000 0111
# third = b'\x8f\x00\x00'    # 1000 1111  0000 0000  0000 0000
#
# t1 = b'this is a test'
# t2 = b'wokka wokka!!!'
#
# print(hamming_distance([first, second, third]))