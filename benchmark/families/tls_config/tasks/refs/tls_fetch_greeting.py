import socket
import ssl


def fetch_greeting(host, port, cafile, server_hostname=None):
    ctx = ssl.create_default_context(cafile=cafile)
    with socket.create_connection((host, port), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=server_hostname or host) as s:
            data = b""
            while len(data) < 4096 and not data.endswith(b"\n"):
                chunk = s.recv(4096 - len(data))
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    data = data[:data.index(b"\n") + 1]
                    break
            return data
