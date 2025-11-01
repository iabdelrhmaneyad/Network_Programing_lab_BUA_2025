import socket
import os

# ---------------------------
# FILE CLIENT (TCP)
# This client connects to the file server and sends a file.
# Steps:
#   1. Send file name
#   2. Send file size
#   3. Send file data in chunks
# ---------------------------

SERVER_IP = "127.0.0.1"   # IP of the file server
SERVER_PORT = 6000        # Port number
BUFFER_SIZE = 4096        # Size of each data chunk
FILENAME = "testfile.bin" # Change to the file you want to send

# Check if the file exists
if os.path.exists(FILENAME):
    filesize = os.path.getsize(FILENAME)

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # The server must kwon what is the file name that will be recived
    # also let's assume that the biggest file name is 100 Char 
    # Step 1: Send the file name (100 bytes, padded with spaces)
    name_to_send = FILENAME.ljust(100)
    client_socket.send(name_to_send.encode("utf-8"))

    # Now the server must know the size of the file that will be recived
    # Step 2: Send the file size (20 bytes, padded with spaces)
    size_to_send = str(filesize).ljust(20)
    client_socket.send(size_to_send.encode("utf-8"))

    # Step 3: Send the file content in chunks
    with open(FILENAME, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)

    print("File sent successfully.")
    client_socket.close()
else:
    print("File not found. Please make sure", FILENAME, "exists.")
