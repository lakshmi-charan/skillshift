import os
import socket
import threading

from sa_testlib import case, need

for _k in list(os.environ):
    if _k.lower() in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
        del os.environ[_k]


class _FakeProxy:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.url = "http://127.0.0.1:%d" % self.sock.getsockname()[1]
        self.seen = []
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                buf = b""
                while b"\r\n\r\n" not in buf:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                if not buf:
                    continue
                self.seen.append(buf.split(b"\r\n\r\n", 1)[0].decode())
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")

    def close(self):
        self.sock.close()


@case("functional")
def t_via_proxy(mod):
    f = need(mod, "make_proxied_client")
    p = _FakeProxy()
    try:
        with f(p.url, "http://inventory.internal/v1") as c:
            assert c.timeout.read == 5.0
            r = c.get("/stock", params={"sku": "A1"})
        assert r.text == "ok"
        head = p.seen[0].split("\r\n")
        assert head[0] == "GET http://inventory.internal/v1/stock?sku=A1 HTTP/1.1", head[0]
        assert any(h.lower() == "user-agent: inventory-sync/1.0" for h in head[1:])
    finally:
        p.close()
