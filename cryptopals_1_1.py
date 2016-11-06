from binascii import *
from base64 import *

message_as_hex = b'49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d'

message_as_binary = unhexlify(message_as_hex)

encoded_message = b64encode(message_as_binary)

print(encoded_message)