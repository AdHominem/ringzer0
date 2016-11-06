from binascii import *
from crypto import *

with open('4.txt') as file, open('/usr/share/dict/american-english') as wordlist_file:

    wordlist = wordlist_file.read()

    # For each line, get the most promising guess
    lines = [break_single_byte_xor(unhexlify(line.strip()))[1] for line in file]

    # Out of these guesses, let's take the best
    best = max(lines, key=lambda line: count_english_words(line, wordlist))

    print(best.decode())
