import socket
import base64
import os
import sys

"""
UDP File Client (Stop-and-Wait)
- Sends GET|<filename> to server.
- Expects OK|<filesize>|<basename> or ERR|<reason>.
- Receives DAT|<seq>|<base64> packets, replies ACK|<seq> for each.
- Finishes on EOF|<next_seq>, replies ACK|EOF.

Usage:
  python file_client_udp.py <server_ip> <filename> [output_path]
Defaults:
  server_ip = 127.0.0.1, port = 5006
If output_path not provided, saves as downloaded_<basename>.
"""

SERVER_PORT = 5006
ACK_TIMEOUT = 5.0


def receive_file(server_ip: str, filename: str, output_path: str | None = None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(ACK_TIMEOUT)

    server = (server_ip, SERVER_PORT)

    # Request file
    sock.sendto(f"GET|{filename}".encode("utf-8"), server)

    try:
        data, _ = sock.recvfrom(2048)
    except socket.timeout:
        print("No response from server.")
        return False

    header = data.decode("utf-8", errors="ignore")
    if header.startswith("ERR|"):
        print(header)
        return False

    if not header.startswith("OK|"):
        print("Unexpected response:", header)
        return False

    _, size_str, basename = header.split("|", 2)
    total_size = int(size_str)
    if not output_path:
        output_path = f"downloaded_{os.path.basename(basename)}"

    # Tell server we are ready
    sock.sendto(b"ACK|START", server)

    received = 0
    expected_seq = 0

    with open(output_path, "wb") as f:
        while received < total_size:
            try:
                pkt, _ = sock.recvfrom(65535)
            except socket.timeout:
                print("Timed out waiting for data. You can re-run to resume (not implemented).")
                return False

            msg = pkt.decode("utf-8", errors="ignore")

            if msg.startswith("DAT|"):
                try:
                    _, seq_str, b64 = msg.split("|", 2)
                    seq = int(seq_str)
                except ValueError:
                    # Malformed; ignore
                    continue

                if seq == expected_seq:
                    chunk = base64.b64decode(b64.encode("ascii"))
                    f.write(chunk)
                    received += len(chunk)
                    sock.sendto(f"ACK|{seq}".encode("utf-8"), server)
                    expected_seq += 1
                elif seq < expected_seq:
                    # Duplicate; re-ack to help server move on
                    sock.sendto(f"ACK|{seq}".encode("utf-8"), server)
                else:
                    # Out of order; ignore (server is stop-and-wait)
                    pass
            elif msg.startswith("EOF|"):
                # End regardless of received count, but prefer correctness
                sock.sendto(b"ACK|EOF", server)
                break
            else:
                # Unknown packet; ignore
                pass

    if received >= total_size:
        print(f"Downloaded {filename} -> {output_path} ({received} bytes)")
        return True
    else:
        print(f"Download incomplete: expected {total_size}, got {received}")
        return False


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    filename = None
    output = None

    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]
    if len(sys.argv) >= 3:
        filename = sys.argv[2]
    if len(sys.argv) >= 4:
        output = sys.argv[3]

    if not filename:
        filename = input("Enter filename to download (relative to server): ").strip()

    ok = receive_file(server_ip, filename, output)
    if not ok:
        sys.exit(1)
