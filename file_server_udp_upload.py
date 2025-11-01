import os
import socket
import base64

"""
UDP File Upload Server (Stop-and-Wait)
- Client initiates: PUT|<basename>|<filesize>
- Server replies: OK or ERR|<reason>
- Client sends chunks: DAT|<seq>|<base64>
- Server replies ACK|<seq> for each valid chunk (duplicates are ACKed)
- Client finishes with: EOF|<seq>; Server replies ACK|EOF

Limitation: handles one upload at a time (simple teaching example).
Port: 5007
Saves files to ./uploads/<basename>
"""

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5007
ACK_TIMEOUT = 2.0
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def serve_once():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print(f"UDP upload server listening on {SERVER_IP}:{SERVER_PORT}")

    expected_seq = None
    remaining = None
    out_file = None
    client = None

    try:
        while True:
            data, addr = sock.recvfrom(65535)
            msg = data.decode("utf-8", errors="ignore")

            if msg.startswith("PUT|"):
                # If currently in a transfer, ignore new PUTs
                if out_file is not None:
                    sock.sendto(b"ERR|Busy", addr)
                    continue

                try:
                    _, name, size_str = msg.split("|", 2)
                    size = int(size_str)
                except Exception:
                    sock.sendto(b"ERR|BadHeader", addr)
                    continue

                safe_name = os.path.basename(name)
                path = os.path.join(UPLOAD_DIR, safe_name)
                try:
                    out_file = open(path, "wb")
                except OSError as e:
                    sock.sendto(f"ERR|{e.__class__.__name__}".encode("utf-8"), addr)
                    out_file = None
                    continue

                client = addr
                expected_seq = 0
                remaining = size
                sock.sendto(b"OK", addr)
                print(f"Receiving {safe_name} ({size} bytes) from {addr}")
                continue

            # If we're in a transfer, only accept data from that client
            if out_file is None or addr != client:
                # Politely reject to other clients
                sock.sendto(b"ERR|NoSession", addr)
                continue

            if msg.startswith("DAT|"):
                try:
                    _, seq_str, b64 = msg.split("|", 2)
                    seq = int(seq_str)
                except ValueError:
                    # malformed
                    continue

                # ACK duplicates to help client progress
                if expected_seq is not None and seq < expected_seq:
                    sock.sendto(f"ACK|{seq}".encode("utf-8"), client)
                    continue

                if expected_seq is not None and seq == expected_seq:
                    try:
                        chunk = base64.b64decode(b64.encode("ascii"))
                    except Exception:
                        continue
                    out_file.write(chunk)
                    remaining -= len(chunk)
                    sock.sendto(f"ACK|{seq}".encode("utf-8"), client)
                    expected_seq += 1
                    continue

                # If seq > expected, ignore (stop-and-wait)
                continue

            if msg.startswith("EOF|"):
                # Accept EOF only when we finished all bytes
                try:
                    _, seq_str = msg.split("|", 1)
                    seq = int(seq_str)
                except ValueError:
                    continue

                if expected_seq is not None and seq == expected_seq and remaining is not None and remaining <= 0:
                    sock.sendto(b"ACK|EOF", client)
                    out_file.close()
                    print(f"Saved to {out_file.name} from {client}")
                    # reset for next client
                    out_file = None
                    expected_seq = None
                    client = None
                    remaining = None
                else:
                    # Not ready to accept EOF; ignore
                    pass
    finally:
        try:
            sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    serve_once()
