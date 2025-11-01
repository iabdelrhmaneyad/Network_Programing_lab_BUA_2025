import socket

# Simple TCP ECHO SERVER
# accepts one client and echoes back whatever it receives

SERVER_IP = "0.0.0.0"
SERVER_PORT = 6000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)

print("TCP server listening on port", SERVER_PORT)

conn, addr = server_socket.accept()
print("Connected by", addr)

while True:
    data = conn.recv(1024)
    if not data:
        break  # client closed
    text = data.decode("utf-8")
    print("Received:", text)
    # TCP guarantees order and delivery (as long as connection is alive)
    conn.sendall(("TCP ECHO: " + text).encode("utf-8"))

conn.close()
server_socket.close()
