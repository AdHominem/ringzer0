import crypto

message = b'1c0111001f010100061a024b53535009181c'
key = b'686974207468652062756c6c277320657965'

print(crypto.xor(message, key))
