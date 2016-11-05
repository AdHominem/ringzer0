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


# (str or bytes) -> bytes
# First we need to interpret the data as hexadecimal
# If we skip this step, the bytes will be encoded separately!
def hex_to_base64(hex_data):
    interpreted = binascii.unhexlify(hex_data)
    return base64.b64encode(interpreted)

