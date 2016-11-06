import hashlib
from itertools import product
import binascii
import string
import converter


# Precomputes hashes and ciphers for cracking
class RainbowTable:
    def __init__(self):
        self.cipher = None
        self.alphabet = None
        self.length = None

    def set_cipher(self, cipher):
        assert type(cipher) == str

        self.cipher = cipher
        print("Cipher set to " + self.cipher)

    def set_alphabet(self, alphabet):
        assert type(alphabet) == str

        self.alphabet = alphabet

    def set_length(self, length):
        assert type(length) == int and length > 0

        self.length = length

    def get_permutations(self):
        assert self.alphabet and self.length

        print("Calculating %d^%d = %d permutations" % (
        self.length, len(self.alphabet), pow(self.length, len(self.alphabet))))
        return [''.join(i) for i in product(self.alphabet, repeat=self.length)]

    def get_table(self):
        assert self.cipher and self.alphabet and self.length

        return {self.use_cipher(word): word for word in self.get_permutations()}

    def use_cipher(self, data):
        assert type(data) == str and self.cipher

        cipher = None
        if self.cipher == 'sha1':
            cipher = hashlib.sha1()

        cipher.update(data.encode())
        return binascii.hexlify(cipher.digest()).decode()


#############################################
# This class assumes you are working with RAW BYTES!
# Make sure that any input is binary data
# Either use literal bytes (b'abcdef')
# Or use the converter class string_to_raw_hex()
#############################################


def xor(message, key):
    assert type(message) == bytes
    assert type(key) == bytearray or type(key) == bytes

    key_as_integer = int.from_bytes(key, byteorder='big') if type(key) == bytearray else int(key, 16)
    message_as_integer = int(message, 16)
    result = message_as_integer ^ key_as_integer

    # Technically it would be okay just to return the hex() value of result, but we want bytes
    # The resulting byte array will have a length of the key if key was a byte array
    # If key is bytes, then it will be half that key's length (one byte has a length of 2!)
    result_length = len(key) if type(key) == bytearray else len(key) // 2

    result_as_bytes = result.to_bytes(result_length, byteorder='big')
    bytes_as_hex = binascii.hexlify(result_as_bytes)
    return bytes_as_hex


def xor_single_byte(message, byte):
    assert type(message) == bytes

    key = generate_keystream_for_(message, byte)
    return xor(message, key)


# The bytestream will have half the length of the message because each byte has a length of 2
def generate_keystream_for_(message, byte):
    assert type(message) == bytes
    return bytearray([byte] * (len(message) // 2))


# This works on raw bytes!
def is_english_sentence(message):
    # If the string is not utf-8, discard it
    try:
        plaintext_interpreted = binascii.unhexlify(message).decode()
    except UnicodeDecodeError:
        return False

    # If it contains non printable chars or no blank space, discard it
    return all(ord(c) < 127 and c in string.printable for c in plaintext_interpreted) \
           and plaintext_interpreted.find(' ') != -1


def crack_single_byte_xor(message):
    for i in range(256):
        plaintext = xor_single_byte(message, i)

        if is_english_sentence(plaintext):
            print("Key %d: Plaintext: %s" % (i, binascii.unhexlify(plaintext).decode()))
