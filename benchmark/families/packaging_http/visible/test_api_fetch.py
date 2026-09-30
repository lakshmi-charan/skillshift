import httpx

from sa_testlib import case, need


@case("fetch_json")
def test_fetch(mod):
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={"q": r.url.params.get("q")}))
    with httpx.Client(base_url="https://api.test", transport=t) as c:
        assert need(mod, "fetch_json")(c, "/search", params={"q": "x"}) == {"q": "x"}


@case("post_json")
def test_post_body(mod):
    seen = []

    def handler(request):
        seen.append(request.content)
        return httpx.Response(201, json={"ok": True})

    with httpx.Client(base_url="https://api.test", transport=httpx.MockTransport(handler)) as c:
        assert need(mod, "post_json")(c, "/orders", {"sku": "A1", "qty": 2}) == {"ok": True}
    assert seen == [b'{"sku": "A1", "qty": 2}']


@case("iter_items")
def test_pages(mod):
    pages = {"/v1/x": {"items": [1], "next": "/x?cursor=2"}, "/v1/x?cursor=2": {"items": [2], "next": None}}

    def handler(request):
        key = request.url.path + ("?" + request.url.query.decode() if request.url.query else "")
        return httpx.Response(200, json=pages[key])

    with httpx.Client(base_url="https://api.test/v1", transport=httpx.MockTransport(handler)) as c:
        assert list(need(mod, "iter_items")(c, "/x")) == [1, 2]
