import json

import httpx

from sa_testlib import case, need


def _client(handler):
    return httpx.Client(base_url="https://api.example.com/v1", transport=httpx.MockTransport(handler))


def _echo(request):
    return httpx.Response(200, json={"path": request.url.path, "params": dict(request.url.params),
                                     "raw_query": request.url.query.decode()})


@case("fetch_json")
def h_fetch_params(mod):
    f = need(mod, "fetch_json")
    with _client(_echo) as c:
        assert f(c, "/users", params={"role": "admin"}) == {"path": "/v1/users", "params": {"role": "admin"},
                                                             "raw_query": "role=admin"}
        assert f(c, "/users")["params"] == {}


@case("fetch_json")
def h_fetch_merges_existing_query(mod):
    f = need(mod, "fetch_json")
    with _client(_echo) as c:
        out = f(c, "/search?q=widgets&sort=asc", params={"limit": 5})
    assert out["params"] == {"q": "widgets", "sort": "asc", "limit": "5"}, out


@case("fetch_json")
def h_fetch_retries(mod):
    f = need(mod, "fetch_json")
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    with _client(handler) as c:
        assert f(c, "/status", retries=2) == {"ok": True} and len(calls) == 3


@case("api_error")
def h_error(mod):
    f, E = need(mod, "fetch_json"), need(mod, "ApiError")
    with _client(lambda r: httpx.Response(404, text="no such user")) as c:
        try:
            f(c, "/users/9")
        except E as e:
            assert e.status_code == 404 and "no such user" in e.body
        else:
            raise AssertionError("expected ApiError")


@case("api_error")
def h_error_after_retries(mod):
    f, E = need(mod, "fetch_json"), need(mod, "ApiError")
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(502, text="bad gateway")

    with _client(handler) as c:
        try:
            f(c, "/x", retries=1)
        except E as e:
            assert e.status_code == 502 and len(calls) == 2
        else:
            raise AssertionError("expected ApiError")


@case("post_json")
def h_post(mod):
    f = need(mod, "post_json")
    seen = {}

    def handler(request):
        seen["ct"] = request.headers["content-type"]
        seen["body"] = json.loads(request.content)
        seen["method"] = request.method
        return httpx.Response(201, json={"id": 7, **seen["body"]})

    with _client(handler) as c:
        out = f(c, "/orders", {"sku": "A1", "qty": 2, "note": "Zoë"})
    assert out == {"id": 7, "sku": "A1", "qty": 2, "note": "Zoë"}
    assert seen["ct"] == "application/json" and seen["method"] == "POST"


@case("post_json")
def h_post_error(mod):
    f, E = need(mod, "post_json"), need(mod, "ApiError")
    with _client(lambda r: httpx.Response(422, json={"error": "qty"})) as c:
        try:
            f(c, "/orders", {"qty": -1})
        except E as e:
            assert e.status_code == 422
        else:
            raise AssertionError("expected ApiError")


def _paged_handler(log):
    data = {1: ["a", "b"], 2: ["c", "d"], 3: ["e"]}

    def handler(request):
        params = request.url.params
        log.append(dict(params))
        if request.url.path != "/v1/tickets":
            return httpx.Response(404, json={"error": "not found"})
        if params.get("status") != "open":
            return httpx.Response(400, json={"error": "status filter required"})
        page = int(params.get("page", "1"))
        nxt = "/tickets?status=open&page=%d" % (page + 1) if page < 3 else None
        return httpx.Response(200, json={"items": data[page], "next": nxt})

    return handler


@case("iter_items")
def h_pages(mod):
    f = need(mod, "iter_items")
    log = []
    with _client(_paged_handler(log)) as c:
        items = list(f(c, "/tickets", params={"status": "open"}))
    assert items == ["a", "b", "c", "d", "e"], items[:10]
    assert len(log) == 3


@case("iter_items")
def h_single_page(mod):
    f = need(mod, "iter_items")
    with _client(lambda r: httpx.Response(200, json={"items": [1, 2], "next": None})) as c:
        assert list(f(c, "/things")) == [1, 2]
