from Crypto.Util.strxor import strxor
from binascii import *

hex_message = b'1c0111001f010100061a024b53535009181c'
hex_key = b'686974207468652062756c6c277320657965'

binary_message = unhexlify(hex_message)
binary_key = unhexlify(hex_key)

cipher_text = strxor(binary_message, binary_key)

cipher_text_as_hex = hexlify(cipher_text)

print(cipher_text_as_hex)
