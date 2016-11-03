import hashlib
import binascii
from timer import Timer
from parser import Parser

parser = Parser(14)
parser.set_cookie('hjldhbibi3daqk7uejm6ip0tu2')
parser.connect()
parser.toggle_debug()

hashtime = Timer("hashing")
parsetime = Timer("parsing")
sendtime = Timer("sending")

messages = parser.get_messages()
message = messages[0]

hashtime.start_timer()
_hash = hashlib.sha512()
_hash.update(message.encode())
digest = _hash.digest()
hashtime.stop_timer()

parsetime.start_timer()
solution = binascii.hexlify(digest).decode()
parsetime.stop_timer()

sendtime.start_timer()
parser.send_solution(solution)
sendtime.stop_timer()

hashtime.print()
parsetime.print()
sendtime.print()