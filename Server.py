import socket
from config import *
from trading_engine import execute_trade

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started on port", PORT)

while True:
    conn, addr = server.accept()
    data = conn.recv(1024).decode()

    print("Received:", data)

    try:
        # Expected format: BUY or SELL
        if data.upper() == "BUY":
            execute_trade("BUY")

        elif data.upper() == "SELL":
            execute_trade("SELL")

        elif data == "/shutdown":
            print("Shutting down server")
            break

    except Exception as e:
        print("Error:", e)

    conn.close()

server.close()