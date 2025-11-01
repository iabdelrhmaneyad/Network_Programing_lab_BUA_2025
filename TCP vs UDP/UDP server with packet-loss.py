import socket
import random

# UDP SERVER with packet-loss simulation

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5005
LOSS_RATE = 0.3   # 30% of packets will be dropped

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print("UDP Loss Server running on port", SERVER_PORT)
print("Simulated loss rate:", int(LOSS_RATE * 100), "%")

while True:
    data, client_addr = server_socket.recvfrom(1024)
    text = data.decode("utf-8")
    print("Received from", client_addr, "->", text)

    # simulate loss
    if random.random() < LOSS_RATE:
        print(">> Simulating PACKET LOSS for this message.")
        # do NOT send reply
        continue

    reply_msg = "ACK: " + text
    server_socket.sendto(reply_msg.encode("utf-8"), client_addr)
    print("Sent reply to", client_addr)
