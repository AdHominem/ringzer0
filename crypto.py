from Crypto.Util.strxor import strxor_c
from binascii import *
from functools import *
import itertools
from converter import *

LETTER_MAP = {
    ' ': 10.74,
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
    'Ñ': 0.00,
    '\x00': 0.00    #This one is included since there will be a null byte padding in the transpose() function
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
    """
    Powerful, but does not work with transposed blocks, so only use this on reassembled text
    :param message:
    :param wordlist:
    :return:
    """
    assert type(message) == bytes

    result = 0

    try:
        words = message.decode().lower().split(' ')
        for word in words:
            result += 1 if word in wordlist else -1
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
            # If ANY non-listed char is encountered, break.
            return 0
    return score


def break_caesar_cipher(string):
    assert type(string) == str

    return [caesar_cipher(string, key) for key in range(26)]


# Determines the quality of a candidate by using the majority of score, deviation and words
# Words will be the fallback in case all are different
def break_single_byte_xor(bytes_data):
    print("-------------------------------")

    candidates = [(key, strxor_c(bytes_data, key)) for key in range(256)]
    # overview = [(candidate, calculate_deviation(candidate[1])) for candidate in candidates]
    # for c, s in overview:
    #     if s < 150:
    #         print(c, s)
    for candidate in candidates:
        score = calculate_score(candidate[1])
        if score > 20:
            print(score, candidate[1], candidate[0])

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


def get_possible_key_sizes(binary_data):
    """
    The precision for get_normalized_hamming_distance can be max for each given keysize instead of setting it to a
    fixed value
    :param binary_data:
    :return:
    """
    best_keysize_and_distance = (1337, 4)
    possible_keysizes = []

    for keysize in range(2, min(len(binary_data) // 2, 41)):
        normalized_hamming_distance = get_normalized_hamming_distance(binary_data, keysize, len(binary_data) // keysize)

        if normalized_hamming_distance < best_keysize_and_distance[1]:
            #print("Found a new best keysize: %d, %f" % (keysize, normalized_hamming_distance))
            possible_keysizes.append(keysize)
            best_keysize_and_distance = (keysize, normalized_hamming_distance)
    return possible_keysizes


def break_multi_byte_xor(binary_data):
    """
    1. Hamming distance: Try all keysizes up until either 40 or a quarter of data length (amount of chunks is 4)
    2. Split the data in chunks of keysize
        If the byte length of the data is not divisible by keysize, this will omit up to keysize - 1 trailing bytes
        Starts at [0, keysize], [keysize, 2 * keysize], [2 * keysize, 3 * keysize], etc...
    3. Transpose blocks: Take the i-th elements of each chunk and join them as a new byte block which is encrypted
            with the same byte
    4. Break the individual blocks and assemble the key
    :param binary_data:
    :return:
    """
    possible_key_sizes = get_possible_key_sizes(binary_data)

    print("\nPossible key sizes based on hamming distance: ", end="")
    print(possible_key_sizes)

    plaintexts = {}
    for keysize in possible_key_sizes[4:]:
        transposed = transpose(binary_data, keysize)
        print("\nTransposed cipher with block length of %d: " % keysize, end="")
        print(transposed)

        tuples = [break_single_byte_xor(block) for block in transposed]
        key = bytes(bytearray([tuple[0] for tuple in tuples]))
        print("The key for a keysize of %d is: " % keysize, end="")
        print(key)

        plaintext = multi_byte_xor(binary_data, key)
        plaintexts[key] = plaintext

    for key in plaintexts:
        #score = calculate_score(plaintexts[key])
        print(key, plaintexts[key])


def transpose(binary_data, length):
    """
    Get a string and break it up into 'length' strings, where each string i is
    composed of every i-1th character.
    """
    chunks = [binary_data[i:i + length] for i in range(0, len(binary_data), length)]
    #print([hexlify(chunk) for chunk in chunks])

    transposed = itertools.zip_longest(*chunks, fillvalue=b'\x00')
    result = [tuple_to_binary_string(tuple) for tuple in transposed]

    return result


def get_hamming_distance(first, second):
    """
    Calculates the hamming distance by looping over all bytes in both strings
    For each of the 8 bit, applies a bit mask and checks if the bits at position i are the same
    If not, increases distance
    :param first: First byte string
    :param second: Second byte string
    :return: The hamming distance between both
    """
    assert len(first) == len(second)
    distance = 0
    for first_byte, second_byte in zip(first, second):
        for i in range(8):
            if (first_byte & 1 << i) != (second_byte & 1 << i):
                distance += 1

    return distance


def get_normalized_hamming_distance(binary_data, keysize, number_of_chunks=4):
    """
    Calculates the normalized hamming distance, that is the average hamming distance per byte.
    A byte string can for a given keysize be separated in chunks of bytes of length keysize
    The average hamming distance between all chunks is calculated and normalized by dividing by keysize
    :param binary_data: A byte string
    :param keysize: The size of the key
    :param number_of_chunks: The number of chunks, this value depends on the keysize so it has to be static.
    Increasing this value increases the precision, its max value is (|string| / keysize)
    :return: The average hamming distance per byte for the given keysize
    """

    # Starts at [0, keysize], [keysize, 2 * keysize], [2 * keysize, 3 * keysize], etc...
    chunks = [binary_data[i * keysize: (i + 1) * keysize] for i in range(number_of_chunks)]

    # To normalize the hamming distance, we compare all chunks with each other
    pairs = list(itertools.combinations(chunks, 2))

    # Calculate the average hamming distance between each pair
    dist = sum([get_hamming_distance(pair[0], pair[1]) for pair in pairs]) / len(pairs)

    # To get the hamming distance per byte, we need to divide by the keysize
    return dist / keysize
