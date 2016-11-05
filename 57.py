import hashlib
import binascii
from timer import Timer
from parser import Parser

parser = Parser(57)
parser.set_cookie('hjldhbibi3daqk7uejm6ip0tu2')
parser.connect()
parser.toggle_debug()

crack = Timer("cracking")
sendtime = Timer("sending")

messages = parser.get_messages()
message = messages[0]
salt = messages[1]

solution = None
crack.go()
for number in range(9999):
    cipher = hashlib.sha1()
    cipher.update(str(number).encode())
    cipher.update(salt.encode())
    if binascii.hexlify(cipher.digest()).decode() == message:
        print("Number: " + str(number))
        solution = str(number)
crack.pause()

sendtime.go()
parser.send_solution(solution)
sendtime.pause()

crack.print()
sendtime.print()