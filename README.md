# Network Programming – Sec3

This folder contains hands‑on Python examples showing UDP vs TCP and simple file transfer patterns in both directions. Use these scripts to see how the socket API works, how reliability differs, and how to run small demos locally on Windows.

## What’s here

- UDP echo demo
  - `udp_server.py` – simple UDP server that prints a message and replies
  - `udp_client.py` – sends a message and prints the reply
- UDP file download (server -> client)
  - `file_server_udp.py` – serves files over UDP (stop‑and‑wait, base64, port 5006)
  - `file_client_udp.py` – downloads a file from the UDP server
- UDP file upload (client -> server)
  - `file_server_udp_upload.py` – receives file uploads via UDP (port 5007) and saves in `uploads/`
  - `file_client_udp_upload.py` – uploads a local file to the UDP server
- TCP file upload (client -> server)
  - `file_server_tcp_upload.py` – accepts TCP uploads (port 6007) and saves in `uploads/`
  - `file_client_tcp_upload.py` – uploads a local file to the TCP server
- Additional TCP example
  - `Sending files TCP/` – an extra simple TCP send example (server/client)

Ports are chosen to avoid conflicts:
- UDP echo: 5005
- UDP download: 5006
- UDP upload: 5007
- TCP upload: 6007

## UDP vs TCP – key differences

- Connection
  - UDP: connectionless. You just send datagrams to an address/port.
  - TCP: connection‑oriented. You `connect()`, then read/write a continuous byte stream.
- Reliability
  - UDP: no guarantees. Packets may be lost, duplicated, or arrive out of order. If you need reliability, you must add it yourself (ACKs, retries, sequencing). Our UDP file transfers use a simple stop‑and‑wait protocol with `ACK` messages and timeouts.
  - TCP: reliable and ordered. The stack handles retransmissions, flow control, and congestion control for you.
- Message boundaries
  - UDP: preserves datagram boundaries. One `recvfrom()` gets one datagram (if not truncated).
  - TCP: stream oriented. You may get partial chunks; you must decide how to frame messages (e.g., length prefix or newline).
- Performance/overhead
  - UDP: lower overhead and latency; great for real‑time media, gaming, or custom protocols.
  - TCP: higher overhead but simpler application logic due to built‑in reliability.

How to observe the difference here:
- Try running the UDP upload while artificially dropping packets (use unstable Wi‑Fi, or quickly toggle the client). You’ll see retries and possibly transfer aborts after many timeouts.
- The TCP upload should complete reliably without custom ACK logic.

## How to run the demos (Windows PowerShell)

Open two terminals in the `sec3` folder. All commands below use relative paths.

### 1) UDP echo

Terminal A – start server:

```powershell
python .\udp_server.py
```

Terminal B – run client:

```powershell
python .\udp_client.py
```

Expected: server prints the received text; client prints the confirmation reply.

### 2) UDP file download (server -> client)

Terminal A – start server:

```powershell
python .\file_server_udp.py
```

Terminal B – download a file that exists in `sec3` (example: `udp_client.py`):

```powershell
python .\file_client_udp.py 127.0.0.1 udp_client.py
```

Expected: saves `downloaded_udp_client.py` and prints the byte count.

### 3) UDP file upload (client -> server)

Terminal A – start server (creates `uploads/` if needed):

```powershell
python .\file_server_udp_upload.py
```

Terminal B – upload a local file from `sec3` (example: `udp_client.py`):

```powershell
python .\file_client_udp_upload.py 127.0.0.1 udp_client.py
```

Expected: server logs receipt and writes `uploads/udp_client.py`.

### 4) TCP file upload (client -> server)

Terminal A – start server:

```powershell
python .\file_server_tcp_upload.py
```

Terminal B – upload a local file:

```powershell
python .\file_client_tcp_upload.py 127.0.0.1 udp_client.py
```

Expected: server saves the exact bytes into `uploads/udp_client.py` and prints “DONE”.

## Python socket API – quick reference

- Create sockets
  - `socket.socket(family, type)` – create a new socket
    - `family`: `AF_INET` (IPv4), `AF_INET6` (IPv6)
    - `type`: `SOCK_DGRAM` (UDP), `SOCK_STREAM` (TCP)

- Server side
  - UDP
    - `bind((host, port))` – start listening for datagrams
    - `recvfrom(bufsize)` – receive one datagram and the sender address
    - `sendto(data, addr)` – send one datagram to the given address
  - TCP
    - `bind((host, port))` – bind to local address
    - `listen(backlog)` – start listening for connections
    - `accept()` – accept one connection, returning `(conn, addr)`
    - `conn.recv(n)` – receive up to `n` bytes
    - `conn.sendall(data)` – send all bytes (retries until done)

- Client side
  - UDP
    - `sendto(data, (host, port))` – send a datagram
    - `recvfrom(bufsize)` – receive a datagram and sender
  - TCP
    - `connect((host, port))` or `create_connection((host, port))`
    - `sendall(data)` / `recv(n)` on the connected socket

- Common utilities
  - `settimeout(seconds)` – make operations raise `socket.timeout` after N seconds
  - `setsockopt(level, opt, value)` – set options (e.g., `SO_REUSEADDR` for TCP servers)
  - `close()` – close the socket
  - `makefile()` – wrap a TCP socket as a file‑like object for `.readline()` etc.

## Troubleshooting

- Windows Firewall may block inbound servers the first time. Allow access when prompted.
- “Address already in use”: a previous server may still be running. Stop it, or change port.
- For TCP, remember it’s a stream: if you expect a line, use newline framing or a length prefix.
- For UDP reliability, expect packet loss. Our UDP demos use simple stop‑and‑wait with `ACK`s; for production you’d want sliding windows, checksums, and congestion handling—or just use TCP.

## Next steps

- Add SHA‑256 checksums to verify integrity after transfers.
- Implement a sliding‑window UDP transfer for higher throughput.
- Add argparse flags (host, port, chunk size) to all scripts.
