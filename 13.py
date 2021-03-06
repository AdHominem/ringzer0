import hashlib
import binascii
from parser import Parser

parser = Parser(13)
parser.set_cookie('hjldhbibi3daqk7uejm6ip0tu2')
parser.connect()
parser.toggle_debug()
messages = parser.get_messages()
message = messages[0]

_hash = hashlib.sha512()
_hash.update(message.encode())
digest = _hash.digest()
solution = binascii.hexlify(digest).decode()

parser.send_solution(solution)
