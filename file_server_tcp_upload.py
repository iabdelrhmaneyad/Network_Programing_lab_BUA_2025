import os
import socket

"""
TCP File Upload Server
- Accepts a connection on port 6007
- Client sends a single header line: PUT|<basename>|<filesize>\n
- Server replies: OK\n or ERR|<reason>\n
- Client then streams <filesize> raw bytes (no base64)
- Server saves to ./uploads/<basename> and replies DONE\n
Handles one client at a time for simplicity.
"""

HOST = "0.0.0.0"
PORT = 6007
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def recv_line(conn) -> str:
    buf = bytearray()
    while True:
        ch = conn.recv(1)
        if not ch:
            break
        buf += ch
        if ch == b"\n":
            break
    return buf.decode("utf-8", errors="ignore").rstrip("\n")


def recv_exact(conn, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.recv(min(65536, n - len(buf)))
        if not chunk:
            raise ConnectionError("Connection closed early")
        buf += chunk
    return bytes(buf)


def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"TCP upload server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected:", addr)
                header = recv_line(conn)
                if not header.startswith("PUT|"):
                    conn.sendall(b"ERR|BadHeader\n")
                    continue
                try:
                    _, name, size_str = header.split("|", 2)
                    size = int(size_str)
                except Exception:
                    conn.sendall(b"ERR|BadHeader\n")
                    continue

                safe = os.path.basename(name)
                path = os.path.join(UPLOAD_DIR, safe)
                try:
                    with open(path, "wb") as f:
                        conn.sendall(b"OK\n")
                        data = recv_exact(conn, size)
                        f.write(data)
                    conn.sendall(b"DONE\n")
                    print(f"Saved to {path} from {addr}")
                except Exception as e:
                    try:
                        conn.sendall(f"ERR|{e.__class__.__name__}\n".encode("utf-8"))
                    except Exception:
                        pass


if __name__ == "__main__":
    serve()
