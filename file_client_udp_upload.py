import os
import socket
import base64
import sys

"""
UDP File Upload Client (Stop-and-Wait)
- Sends header: PUT|<basename>|<filesize>
- Waits for OK
- Sends data packets: DAT|<seq>|<base64>; waits for ACK|<seq> before next (retry on timeout)
- Finishes with EOF|<seq> and waits for ACK|EOF

Usage:
  python file_client_udp_upload.py <server_ip> <path_to_file>
Defaults: server_ip=127.0.0.1, port=5007
"""

SERVER_PORT = 5007
CHUNK_SIZE = 1024
ACK_TIMEOUT = 1.0
MAX_RETRIES = 10


def upload(server_ip: str, file_path: str):
    basename = os.path.basename(file_path)
    size = os.path.getsize(file_path)

    server = (server_ip, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send header
    sock.sendto(f"PUT|{basename}|{size}".encode("utf-8"), server)

    sock.settimeout(3.0)
    try:
        resp, _ = sock.recvfrom(1024)
    except socket.timeout:
        print("No response from server.")
        return False

    if resp.decode("utf-8", errors="ignore") != "OK":
        print("Server responded:", resp.decode("utf-8", errors="ignore"))
        return False

    print(f"Uploading {basename} ({size} bytes) -> {server_ip}:{SERVER_PORT}")

    seq = 0
    sent = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            b64 = base64.b64encode(chunk).decode("ascii")
            packet = f"DAT|{seq}|{b64}".encode("utf-8")
            expect_ack = f"ACK|{seq}".encode("utf-8")

            retries = 0
            while retries < MAX_RETRIES:
                sock.sendto(packet, server)
                sock.settimeout(ACK_TIMEOUT)
                try:
                    ack, _ = sock.recvfrom(1024)
                    if ack == expect_ack:
                        break
                except socket.timeout:
                    retries += 1
            else:
                print(f"Failed waiting for ACK for seq {seq}")
                return False

            sent += len(chunk)
            seq += 1

    # Send EOF
    eof = f"EOF|{seq}".encode("utf-8")
    retries = 0
    while retries < MAX_RETRIES:
        sock.sendto(eof, server)
        sock.settimeout(ACK_TIMEOUT)
        try:
            ack, _ = sock.recvfrom(1024)
            if ack.decode("utf-8", errors="ignore") == "ACK|EOF":
                print(f"Upload complete: {sent} bytes sent")
                return True
        except socket.timeout:
            retries += 1

    print("Failed to finalize upload (EOF not acknowledged)")
    return False


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    path = None

    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]
    if len(sys.argv) >= 3:
        path = sys.argv[2]

    if not path:
        path = input("Path of local file to upload: ").strip()

    if not os.path.exists(path) or not os.path.isfile(path):
        print("File does not exist:", path)
        sys.exit(1)

    ok = upload(server_ip, path)
    if not ok:
        sys.exit(1)
