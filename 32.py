from parser import Parser

parser = Parser(32)
parser.set_cookie('')
parser.connect()
message = parser.get_message().split(' ')

decimal = int(message[0])
hex = int(message[2], 16)
binary = int(message[4], 2)

solution = decimal + hex - binary

parser.send_solution(solution)
