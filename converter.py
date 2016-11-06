import base64
import binascii


# Class for various conversion, mostly between ascii, binary and hex
# Functions in this class use raw binary data only

# unhexlify - interprets the hex values of all bytes inside a string / bytes
# b64encode - encodes bytes with base64


def ascii_to_binary_string(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def binary_string_to_ascii(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return integer_to_bytes_array(n).decode(encoding, errors)


def integer_to_bytes_array(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


def string_to_raw_hex(message):
    message_as_bytes = message.encode()
    bytes_as_hex = binascii.hexlify(message_as_bytes)
    return bytes_as_hex


def raw_hex_to_string(message):
    interpreted = binascii.unhexlify(message)
    decoded = interpreted.decode(errors='ignore')
    return decoded


def hex_string_to_raw_hex(message):
    return message.strip().encode()


# Turns hex data (either as ascii string or as hex bytes) into bytes
# '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'
# -> b'\x1b77316?x\x15\x1b\x7f+x413=x9x(7-6<x7>x:9;76'
def hex_string_to_bytes(message):
    return binascii.unhexlify(message.strip())


# (str or bytes) -> bytes
# First we need to interpret the data as hexadecimal
# If we skip this step, the bytes will be encoded separately!
def hex_to_base64(hex_data):
    interpreted = binascii.unhexlify(hex_data)
    return base64.b64encode(interpreted)

