import socket

# TCP CLIENT
# connects to TCP server and sends few messages

SERVER_IP = "127.0.0.1"
SERVER_PORT = 6000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Connected to TCP server")
except Exception as e:
    print("Could not connect:", e)
else:
    for i in range(1, 6):
        msg = f"hello tcp {i}"
        client_socket.sendall(msg.encode("utf-8"))
        data = client_socket.recv(1024)
        print("Server reply:", data.decode("utf-8"))

    client_socket.close()
