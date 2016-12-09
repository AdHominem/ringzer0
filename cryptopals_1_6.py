from crypto import *
from base64 import b64decode

with open('6.txt') as file:
    message = file.read()

decoded = b64decode(message)

keysize = min(range(2, min(len(decoded)/4, 41)),key=lambda ks: get_normalized_hamming_distance(decoded, ks))
print(keysize)

result = break_multi_byte_xor(decoded)


