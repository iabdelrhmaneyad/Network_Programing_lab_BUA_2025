import os
import socket
import sys

"""
TCP File Upload Client
- Connects to server at port 6007
- Sends header: PUT|<basename>|<filesize>\n
- Waits for OK\n then streams raw bytes
- On success, expects DONE\n
Usage:
  python file_client_tcp_upload.py <server_ip> <path_to_file>
Defaults: server_ip=127.0.0.1
"""

PORT = 6007


def upload(server_ip: str, file_path: str):
    basename = os.path.basename(file_path)
    size = os.path.getsize(file_path)

    with socket.create_connection((server_ip, PORT), timeout=5) as s:
        header = f"PUT|{basename}|{size}\n".encode("utf-8")
        s.sendall(header)
        resp = s.makefile("rb", buffering=0)
        line = resp.readline().decode("utf-8", errors="ignore").rstrip("\n")
        if line != "OK":
            print("Server responded:", line)
            return False
        print(f"Uploading {basename} ({size} bytes) -> {server_ip}:{PORT}")
        with open(file_path, "rb") as f:
            s.sendall(f.read())
        line = resp.readline().decode("utf-8", errors="ignore").rstrip("\n")
        if line == "DONE":
            print("Upload complete (TCP)")
            return True
        else:
            print("Unexpected response:", line)
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
