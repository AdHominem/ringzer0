import hashlib
from itertools import product
import binascii


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

        print("Calculating %d^%d = %d permutations" % (self.length, len(self.alphabet), pow(self.length, len(self.alphabet))))
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

