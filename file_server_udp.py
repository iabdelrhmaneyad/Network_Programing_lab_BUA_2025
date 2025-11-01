import os
import socket
import base64
import threading

"""
UDP File Server (Stop-and-Wait)
- Listens for GET|<filename> requests.
- Responds with OK|<filesize>|<basename> or ERR|<reason>.
- Sends file in base64-encoded chunks: DAT|<seq>|<payload>.
- Waits for ACK|<seq> after each chunk (stop-and-wait).
- Finishes with EOF|<next_seq> and expects ACK|EOF.

Note: This is a teaching example. It's simple and supports one transfer at a time per client.
Port: 5006 (to avoid clashing with simple UDP example on 5005)
"""

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5006
CHUNK_SIZE = 1024  # raw bytes before base64
ACK_TIMEOUT = 1.0  # seconds
MAX_RETRIES = 10


def send_with_ack(sock: socket.socket, packet: bytes, expect_ack: str, client_addr):
    """Send a packet and wait for a specific ack string. Retries on timeout.
    Returns True if ack received, False otherwise.
    """
    retries = 0
    while retries < MAX_RETRIES:
        sock.sendto(packet, client_addr)
        sock.settimeout(ACK_TIMEOUT)
        try:
            ack, _ = sock.recvfrom(4096)
            if ack.decode("utf-8", errors="ignore") == expect_ack:
                return True
        except socket.timeout:
            retries += 1
    return False


def handle_get(sock: socket.socket, client_addr, filename: str):
    # Normalize and keep inside current directory
    safe_name = os.path.basename(filename)
    if not os.path.exists(safe_name) or not os.path.isfile(safe_name):
        err = f"ERR|NotFound|{safe_name}"
        sock.sendto(err.encode("utf-8"), client_addr)
        return

    filesize = os.path.getsize(safe_name)
    ok_msg = f"OK|{filesize}|{safe_name}".encode("utf-8")
    sock.sendto(ok_msg, client_addr)

    # Wait for client ready
    sock.settimeout(ACK_TIMEOUT)
    try:
        ready, _ = sock.recvfrom(1024)
        if ready.decode("utf-8", errors="ignore") != "ACK|START":
            return
    except socket.timeout:
        return

    seq = 0
    with open(safe_name, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            b64 = base64.b64encode(chunk).decode("ascii")
            packet = f"DAT|{seq}|{b64}".encode("utf-8")
            expect_ack = f"ACK|{seq}"
            ok = send_with_ack(sock, packet, expect_ack, client_addr)
            if not ok:
                print(f"Transfer aborted to {client_addr}: no ACK for seq {seq}")
                return
            seq += 1

    # End of file
    eof_msg = f"EOF|{seq}".encode("utf-8")
    ok = send_with_ack(sock, eof_msg, "ACK|EOF", client_addr)
    if not ok:
        print(f"Client {client_addr} did not ACK EOF for {safe_name}")
    else:
        print(f"Sent {safe_name} ({filesize} bytes) to {client_addr}")


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print(f"UDP file server listening on {SERVER_IP}:{SERVER_PORT}")
    while True:
        data, addr = sock.recvfrom(8192)
        msg = data.decode("utf-8", errors="ignore")
        if msg.startswith("GET|"):
            _, name = msg.split("|", 1)
            t = threading.Thread(target=handle_get, args=(sock, addr, name), daemon=True)
            t.start()
        else:
            sock.sendto(b"ERR|UnknownCommand", addr)


if __name__ == "__main__":
    start_server()