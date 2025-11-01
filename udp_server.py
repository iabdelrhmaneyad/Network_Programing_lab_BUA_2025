import socket

# ---------------------------
# UDP SERVER
# This program creates a UDP server that waits for incoming messages
# from any client, prints them, and replies with a confirmation message.
# ---------------------------

# Server configuration
SERVER_IP = "0.0.0.0"     # Listen on all available network interfaces
SERVER_PORT = 5005        # Server port number

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP address and port
server_socket.bind((SERVER_IP, SERVER_PORT))

print("UDP server is running and waiting for messages...")

# Infinite loop to keep receiving messages
while True:
    # Receive data (up to 1024 bytes) and get client address
    data, client_addr = server_socket.recvfrom(1024)
    text = data.decode("utf-8")
    print("Received from", client_addr, "->", text)

    # Send a reply message back to the client
    reply_msg = "Message received by UDP server"
    server_socket.sendto(reply_msg.encode("utf-8"), client_addr)
