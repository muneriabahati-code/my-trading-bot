import socket
import sys
from config import HOST

PORT = int(sys.argv[1])
MESSAGE = sys.argv[2]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))
client.send(MESSAGE.encode())

client.close()