import httpx

from sa_testlib import case, need


@case("base_config")
def test_base_url(mod):
    t = httpx.MockTransport(lambda r: httpx.Response(200, text=str(r.url)))
    with need(mod, "make_client")("https://svc.internal", transport=t) as c:
        assert c.get("/ping").text == "https://svc.internal/ping"


@case("proxy_routing")
def test_proxy_accepted(mod):
    with need(mod, "make_client")("https://svc.internal", proxy_url="http://proxy.corp:3128") as c:
        assert c.base_url == httpx.URL("https://svc.internal")


@case("wsgi_client")
def test_wsgi(mod):
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"hello"]

    with need(mod, "make_wsgi_client")(app) as c:
        assert c.get("/").text == "hello"
