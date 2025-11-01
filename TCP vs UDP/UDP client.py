import socket

# UDP CLIENT to test packet loss
# Sends many messages and waits for reply
# If no reply is received within timeout -> we say "maybe lost"

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# if no data within 1 second -> raise socket.timeout
client_socket.settimeout(1.0)

total_sent = 20
received_count = 0

for i in range(1, total_sent + 1):
    msg = f"msg {i}"
    client_socket.sendto(msg.encode("utf-8"), (SERVER_IP, SERVER_PORT))
    print("Sent:", msg)

    try:
        data, server_addr = client_socket.recvfrom(1024)
        print("  -> got reply:", data.decode("utf-8"))
        received_count += 1
    except socket.timeout:
        # this is the IMPORTANT :
        # UDP does not guarantee delivery → no reply
        print("  -> NO reply (timeout) → possible packet loss")

client_socket.close()

print("\n=== UDP TEST SUMMARY ===")
print("Total sent:", total_sent)
print("Total replies received:", received_count)
print("Observed loss:", total_sent - received_count)
