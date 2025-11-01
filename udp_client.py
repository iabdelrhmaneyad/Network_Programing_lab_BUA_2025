import socket

# ---------------------------
# UDP CLIENT
# This program sends a message to the UDP server
# and waits for a reply. Note: UDP is connectionless.
# ---------------------------

SERVER_IP = "127.0.0.1"   # IP of the UDP server
SERVER_PORT = 5005        # Port of the UDP server

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the message to send
msg = "Hello from UDP client"

# Send message to the server
client_socket.sendto(msg.encode("utf-8"), (SERVER_IP, SERVER_PORT))
print("Message sent to UDP server")

# Wait for a reply from the server
data, server_addr = client_socket.recvfrom(1024)
print("Reply from server:", data.decode("utf-8"))
