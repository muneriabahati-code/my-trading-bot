import socket
import threading
from config import *
from trading_engine import execute_trade

# Function to handle each signal independently
def handle_client(conn, addr):
    with conn: # This automatically closes the connection when done
        try:
            # .strip() removes any hidden spaces or newlines sent over the network
            data = conn.recv(1024).decode('utf-8').strip()
            print(f"[{addr}] Received Signal: {data}")

            if data.upper() == "BUY":
                conn.sendall(b"ACK: BUY command accepted\n")
                execute_trade("BUY")
            
            elif data.upper() == "SELL":
                conn.sendall(b"ACK: SELL command accepted\n")
                execute_trade("SELL")
                
            elif data.upper() == "/SHUTDOWN":
                conn.sendall(b"ACK: SHUTDOWN command accepted\n")
                print("Shutdown command received (Warning: this only stops this thread)")
            else:
                print(f"⚠️ Unknown command ignored: {data}")
                conn.sendall(b"ERROR: Unknown command\n")

        except Exception as e:
            print(f"🚨 Error handling connection from {addr}: {e}")
            try:
                conn.sendall(f"ERROR: {e}\n".encode('utf-8'))
            except Exception:
                pass

# Main server function
def start_server():
    # 'with' ensures the server socket cleans up properly
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        
        # Prevent the annoying "Address already in use" error if you restart quickly
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server.bind((HOST, PORT))
        server.listen()
        print(f"🚀 High-Speed Trading Server listening on {HOST}:{PORT}")

        try:
            while True:
                conn, addr = server.accept()
                
                # Hand the signal off to a new thread so the server can keep listening instantly
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True # Allows the script to exit cleanly
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server manually...")
        except Exception as e:
            print(f"🚨 Critical Server Error: {e}")

if __name__ == "__main__":
    start_server()
