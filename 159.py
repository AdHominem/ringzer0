import hashlib
import binascii

import itertools

from timer import Timer
from parser import Parser
import string

crack = Timer("cracking")
sendtime = Timer("sending")

parser = Parser(159)
parser.set_cookie('fdlhp5k1oir35tp771tfuou527')
parser.connect()
parser.toggle_debug()

messages = parser.get_messages()
hash_value = messages[0]

crack.go()
generator = itertools.product(string.ascii_lowercase + '0123456789', repeat=6)

attempt = None
while True:
    try:
        attempt = ''.join(generator.__next__())
        cipher = hashlib.sha1()
        cipher.update(attempt.encode())
        if binascii.hexlify(cipher.digest()).decode() == hash_value:
            print("Found the message: %s" % attempt)
            break
    except StopIteration:
        exit("Value not in this generator")
crack.pause()

sendtime.go()
parser.send_solution(attempt)
sendtime.pause()

crack.print()
sendtime.print()
