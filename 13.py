import hashlib
import binascii
from parser import Parser

parser = Parser(13)
parser.set_cookie('')
parser.connect()
message = parser.get_message()

_hash = hashlib.sha512()
_hash.update(message.encode())
digest = _hash.digest()
solution = binascii.hexlify(digest).decode()

parser.send_solution(solution)
