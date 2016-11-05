import hashlib
import binascii
from timer import Timer
from parser import Parser
import converter

parser = Parser(121)
parser.set_cookie('kbiourgl1oi6tdun0dbkeq3mb5')
parser.connect()
parser.toggle_debug()

hashtime = Timer("hashing")
parsetime = Timer("parsing")
sendtime = Timer("sending")

parsetime.go()
messages = parser.get_messages()
shellcode = messages[0]
parsetime.pause()

hashtime.go()
_hash = hashlib.sha512()
_hash.update(message.encode())
digest = _hash.digest()
hashtime.pause()

parsetime.go()
solution = binascii.hexlify(digest).decode()
parsetime.pause()

sendtime.go()
parser.send_solution(solution)
sendtime.pause()

hashtime.print()
parsetime.print()
sendtime.print()