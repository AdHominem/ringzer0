from converter import *
import crypto
import binascii

# with open('4.txt') as file:
#
#     for line in file:
#         line_as_bytes = hex_string_to_bytes(line)
#         breakSingleByteXOR(line_as_bytes)


def decode_lines(filename):
    f = open(filename, 'r')
    for line in f:
        if line[-1] == '\n':
            line = line[:-1]
        s = binascii.unhexlify(line)
        yield s


def find_single_byte_xor(lines):
    broken_lines = [crypto.break_single_byte_xor(l)[1] for l in lines]

    def score(i):
        return crypto.calculate_score(broken_lines[i])
    max_i = max(range(len(broken_lines)), key=score)
    return max_i + 1, broken_lines[max_i]

print(find_single_byte_xor(decode_lines('4.txt')))
