import json
import os
import socket
import threading

import httpx

from sa_testlib import case, need

for _k in list(os.environ):
    if _k.lower() in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
        del os.environ[_k]


class _FakeProxy:
    """Minimal HTTP forward proxy on 127.0.0.1 that records request lines and answers itself."""

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
                self.seen.append(buf.split(b"\r\n", 1)[0].decode())
                body = b"via-proxy"
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\nConnection: close\r\n\r\n%s" % (len(body), body))

    def close(self):
        self.sock.close()


def _echo(request):
    return httpx.Response(200, json={"url": str(request.url), "headers": dict(request.headers)})


@case("base_config")
def h_base_url_headers(mod):
    f = need(mod, "make_client")
    with f("https://api.internal/v2", headers={"X-Team": "billing"}, transport=httpx.MockTransport(_echo)) as c:
        data = c.get("/invoices", params={"page": 1}).json()
    assert data["url"] == "https://api.internal/v2/invoices?page=1"
    assert data["headers"]["x-team"] == "billing"


@case("base_config")
def h_timeout(mod):
    f = need(mod, "make_client")
    with f("https://api.internal", timeout=3.5, transport=httpx.MockTransport(_echo)) as c:
        assert c.timeout.read == 3.5 and c.timeout.connect == 3.5
    with f("https://api.internal", transport=httpx.MockTransport(_echo)) as c:
        assert c.timeout.read == 10.0


@case("proxy_routing")
def h_proxy(mod):
    f = need(mod, "make_client")
    p = _FakeProxy()
    try:
        with f(proxy_url=p.url) as c:
            r = c.get("http://inventory.internal/health")
        assert r.status_code == 200 and r.text == "via-proxy"
        assert p.seen == ["GET http://inventory.internal/health HTTP/1.1"], p.seen
    finally:
        p.close()


@case("proxy_routing")
def h_proxy_with_base_url(mod):
    f = need(mod, "make_client")
    p = _FakeProxy()
    try:
        with f("http://billing.internal/api", proxy_url=p.url, headers={"X-A": "1"}) as c:
            r = c.post("/charge", json={"amount": 5})
        assert r.text == "via-proxy"
        assert p.seen == ["POST http://billing.internal/api/charge HTTP/1.1"], p.seen
    finally:
        p.close()


@case("proxy_routing")
def h_no_proxy_direct(mod):
    f = need(mod, "make_client")
    with f("https://api.internal", transport=httpx.MockTransport(_echo)) as c:
        assert c.get("/x").json()["url"] == "https://api.internal/x"


def _wsgi_app(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length) if length else b""
    payload = {"method": environ["REQUEST_METHOD"], "path": environ["PATH_INFO"],
               "query": environ.get("QUERY_STRING", ""), "body": body.decode(),
               "token": environ.get("HTTP_X_TOKEN")}
    status = "404 Not Found" if environ["PATH_INFO"] == "/missing" else "200 OK"
    start_response(status, [("Content-Type", "application/json"), ("X-App", "demo")])
    return [json.dumps(payload).encode()]


@case("wsgi_client")
def h_wsgi_get(mod):
    f = need(mod, "make_wsgi_client")
    with f(_wsgi_app) as c:
        r = c.get("/items", params={"q": "a"})
    assert r.status_code == 200 and r.headers["x-app"] == "demo"
    assert r.json()["path"] == "/items" and r.json()["query"] == "q=a" and r.json()["method"] == "GET"


@case("wsgi_client")
def h_wsgi_post_headers(mod):
    f = need(mod, "make_wsgi_client")
    with f(_wsgi_app, headers={"X-Token": "t0k"}) as c:
        r = c.post("/submit", content=b"hello")
        miss = c.get("/missing")
    assert r.json()["body"] == "hello" and r.json()["token"] == "t0k" and r.json()["method"] == "POST"
    assert miss.status_code == 404


@case("wsgi_client")
def h_wsgi_base_url(mod):
    f = need(mod, "make_wsgi_client")
    with f(_wsgi_app, base_url="http://app.local") as c:
        r = c.get("/ping")
    assert str(r.request.url) == "http://app.local/ping"


@case("error_hook")
def h_raise_errors(mod):
    f = need(mod, "make_client")
    t = httpx.MockTransport(lambda req: httpx.Response(503 if req.url.path == "/down" else 200, text="x"))
    with f("https://svc", raise_errors=True, transport=t) as c:
        assert c.get("/ok").status_code == 200
        try:
            c.get("/down")
        except httpx.HTTPStatusError as e:
            assert e.response.status_code == 503
        else:
            raise AssertionError("expected HTTPStatusError")


@case("error_hook")
def h_no_raise_by_default(mod):
    f = need(mod, "make_client")
    t = httpx.MockTransport(lambda req: httpx.Response(500))
    with f("https://svc", transport=t) as c:
        assert c.get("/boom").status_code == 500
