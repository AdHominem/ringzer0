from Crypto.Util.strxor import strxor
from converter import *

message = '1c0111001f010100061a024b53535009181c'
key = '686974207468652062756c6c277320657965'

print(binascii.hexlify(strxor(hex_string_to_bytes(message), hex_string_to_bytes(key))))
