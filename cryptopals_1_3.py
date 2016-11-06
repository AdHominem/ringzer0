from crypto import  *
from converter import *
message = b'1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'
print(break_single_byte_xor(hex_string_to_bytes(message)))

