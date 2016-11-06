import crypto
import binascii
import string

message = '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'

for i in range(128):
    key = bytearray([i] * (len(message) // 2))
    xor = crypto.xor(message, key)
    result = binascii.unhexlify(xor)
    if all(ord(c) < 127 and c in string.printable for c in result.decode()):
        print(str(i) + ":" + result.decode())
