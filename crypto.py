import itertools
import math
import random
#from Crypto.Util.strxor import strxor_c
from converter import *
from timer import measure


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
    return 0
    # print("-------------------------------")
    #
    # candidates = [(key, strxor_c(bytes_data, key)) for key in range(256)]
    # # overview = [(candidate, calculate_deviation(candidate[1])) for candidate in candidates]
    # # for c, s in overview:
    # #     if s < 150:
    # #         print(c, s)
    # for candidate in candidates:
    #     score = calculate_score(candidate[1])
    #     if score > 20:
    #         print(score, candidate[1], candidate[0])
    #
    # score = max(candidates, key=lambda x: calculate_score(x[1]))
    # return score
    # # deviation = min(candidates, key=lambda x: calculate_deviation(x[1]))
    # # if score == deviation:
    # #     return score
    # #
    # # with open('/usr/share/dict/american-english') as file:
    # #     wordlist = file.read()
    # # words = max(candidates, key=lambda candidate: count_english_words(candidate[1], wordlist))
    # #
    # # return words


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


# Math


def gcd(first, second):
    bigger = first if first > second else second
    smaller = first if first < second else second
    return bigger if smaller == 0 else gcd(smaller, bigger % smaller)


# Uses the decomposition theorem of an odd prime candidate number
# For a given integer a, tries to determine if number is composite
def is_composite(a, odd_part, number, exponent):
    if pow(a, odd_part, number) == 1:
        return False
    for i in range(exponent):
        if pow(a, 2**i * odd_part, number) == number-1:
            return False
    return True


# Miller Rabin
# Extends the decomposition theorem to a number of a's.
# All necessary as are checked to determine if number is composite
# If none, the number is probably prime
def is_prime(number, security_parameter = 11):
    assert security_parameter > 0

    if number in (0, 1):
        return True

    odd_part = number - 1
    exponent = 0
    while not odd_part % 2:
        odd_part >>= 1
        exponent += 1

    if number < 1373653:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3))
    if number < 25326001:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5))
    if number < 118670087467:
        if number == 3215031751:
            return False
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7))
    if number < 2152302898747:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11))
    if number < 3474749660383:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11, 13))
    if number < 341550071728321:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11, 13, 17))
    if number < 3825123056546413051:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11, 13, 17, 19, 23))
    if number < 318665857834031151167461:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37))
    if number < 3317044064679887385961981:
        return not any(is_composite(a, odd_part, number, exponent) for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41))

    for i in range(security_parameter):
        a = random.randint(2, number - 2)
        if is_composite(a, odd_part, number, exponent):
            return False
    return True


# Generates a random prime of at least limit size
def generate_prime(limit):
    # Make sure the limit is odd
    if limit % 2 == 0:
        limit += 1

    while not is_prime(limit):
        limit += 2
    return limit


def phi(number):
    if is_prime(number):
        return number - 1

    result = 0
    for i in range(number):
        if gcd(i, number) == 1:
            result += 1

    return result


# a is the modulus
# returns (gcd, x, y), where y is the inverse of b
def eea(a, b):
    if a == 0:
        return b, 0, 1
    else:
        remainder = b % a
        quotient = b // a
        gcd, x, y = eea(remainder, a)

        #print("\t\t".join([str(i) for i in [a, b, "%d %% %d = %d" % (b, a, remainder), "%d / %d = %d" % (b, a, quotient), x, y]]))

        return gcd, y - quotient * x, x


def inverse(number, modulus):
    result = eea(modulus, number)
    if result[0] != 1:
        raise ValueError('There is no inverse if the number is not coprime to the modulus')
    else:
        return result[2] if result[2] > 0 else result[2] + modulus


def crt(moduli, numbers):
    product_of_moduli = 1
    result = 0
    for i in range(len(numbers)):
        product_of_moduli *= moduli[i]

    for i in range(len(numbers)):
        p = product_of_moduli // moduli[i]
        result += numbers[i] * inverse(p, moduli[i]) * p
    return result % product_of_moduli


# ECC


def ec_addition(x1, y1, x2, y2, p):
    assert x1 != x2 or y1 != y2

    s = (y2 - y1) * brute_force_inverse(x2 - x1, p) % p
    x3 = (pow(s, 2) - x1 - x2) % p
    return x3, (s * (x1 - x3) - y1) % p


def ec_double(x, y, p, a):
    s = (3 * pow(x, 2) + a) * brute_force_inverse(2 * y, p) % p
    new_x = (pow(s, 2) - 2 * x) % p
    return new_x, (s * (x - new_x) - y) % p


def brute_force_inverse(number, group):
    factor = 1
    while (number * factor) % group != 1:
        factor += 1
    return factor


def calculate_points(a, p, x1, y1, x2, y2, recursion=2):
    if x1 == x2 and y2 == p - y1:
        print(recursion, "P = O")
        return
    if x1 == x2 and y1 == y2:
        x3, y3 = ec_double(x1, y1, p, a)
    else:
        x3, y3 = ec_addition(x1, y1, x2, y2, p)
    print(recursion, "P =", (x3, y3))
    return calculate_points(a, p, x1, y1, x3, y3, recursion + 1)


# RSA


class RSA:
    def __init__(self, p, q):
        assert is_prime(p)
        assert is_prime(q)

        self.p = p
        self.q = q
        self.n = p * q
        self.m = (p-1) * (q-1)

        print(self.n, self.m)

        # Preferably use 3, 17 or 2^16 + 1
        if gcd(self.m, 3) == 1:
                self.e = 3
        elif gcd(self.m, 17) == 1:
                self.e = 17
        elif gcd(self.m, 2**16 + 1) == 1:
                self.e = 2**16 + 1
        else:
            for e in range(2, self.m):
                if gcd(self.m, e) == 1:
                    self.e = e
                    break

        print(self.e)
        self.d = inverse(self.e, self.m)
        print(self.d)

    def encrypt(self, plaintext):
        """
        Encrypts a byte string using the RSA parameters
        :param plaintext: The string to encrypt
        :return: An encrypted string as bytes
        """
        assert type(plaintext) == bytes
        bitlength_n = math.ceil(math.log2(self.n))
        message = int.from_bytes(plaintext, byteorder="big")
        bitlength_message = math.ceil(math.log2(message))

        try:
            assert bitlength_message <= bitlength_n
        except AssertionError:
            print("Error! You can not encrypt a %d bit message with a %d bit modulus!" % (bitlength_message, bitlength_n))
            exit(1)

        cipher = pow(message, self.d, self.n)
        return int.to_bytes(cipher, byteorder="big", length=math.ceil(math.log(cipher, 256)))

    def decrypt(self, ciphertext):
        """
        Encrypts a byte string using the RSA parameters
        :param ciphertext: The string to encrypt
        :return: An encrypted string as bytes
        """
        assert type(ciphertext) == bytes

        message = int.from_bytes(ciphertext, byteorder="big")
        plaintext = pow(message, self.e, self.n)
        return int.to_bytes(plaintext, byteorder="big", length=math.ceil(math.log(plaintext, 256)))

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


p = measure(generate_prime, 2**random.randint(1024, 1064))
q = measure(generate_prime, 2**random.randint(1024, 1064))
print(p)
print(q)

rsa = RSA(p, q)
cipher = rsa.encrypt(b"Hello World, how are you today?")
print(cipher)

decrypted = rsa.decrypt(cipher)
print(decrypted)
