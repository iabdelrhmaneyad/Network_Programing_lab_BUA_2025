import socket
import os

# ---------------------------
# FILE SERVER (TCP)
# This server receives a binary file from a client.
# Steps:
#   1. Receive the file name
#   2. Receive the file size
#   3. Receive the file data in chunks and save it locally
# ---------------------------

SERVER_IP = "0.0.0.0"      # Listen on all interfaces
SERVER_PORT = 6000         # Port number
BUFFER_SIZE = 4096         # Size of each data chunk

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind and listen for connections
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)
print("File server is listening on port", SERVER_PORT)

# Accept a connection
conn, client_addr = server_socket.accept()
print("Connected by", client_addr)

# Step 1: Receive file name (fixed length: 100 bytes)
filename_bytes = conn.recv(100)
filename = filename_bytes.decode("utf-8").strip()
print("Incoming file name:", filename)

# Step 2: Receive file size (fixed length: 20 bytes)
filesize_bytes = conn.recv(20)
filesize_str = filesize_bytes.decode("utf-8").strip()
filesize = int(filesize_str)
print("Incoming file size:", filesize, "bytes")

# Step 3: Receive the file data and write to disk
received = 0
with open("received_" + filename, "wb") as f:
    while received < filesize:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        f.write(data)
        received += len(data)
        print("Received:", received, "/", filesize)

print("File received successfully and saved as:", "received_" + filename)

# Close connections
conn.close()
server_socket.close()
