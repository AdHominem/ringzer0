from binascii import *

from crypto import *

message_hex = b'1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'

message_bin = unhexlify(message_hex)

print(break_single_byte_xor(message_bin))
