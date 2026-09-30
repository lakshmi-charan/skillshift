import httpx

from sa_testlib import case, need

PAGES = {None: ["Login fails", "Crash on save"], "c2": ["Typo in footer"], "c3": ["Slow search"]}
NEXT = {None: "c2", "c2": "c3", "c3": None}


def _client(log):
    def handler(request):
        p = request.url.params
        log.append(dict(p))
        if request.url.path != "/api/tickets":
            return httpx.Response(404, json={"error": "not found"})
        if p.get("status") != "open" or p.get("project") != "web":
            return httpx.Response(400, json={"error": "status and project are required"})
        cur = p.get("cursor")
        nxt = NEXT[cur]
        return httpx.Response(200, json={"items": [{"title": t} for t in PAGES[cur]],
                                         "next": ("/tickets?cursor=%s" % nxt) if nxt else None})
    return httpx.Client(base_url="https://tracker.example/api", transport=httpx.MockTransport(handler))


@case("functional")
def t_all_pages(mod):
    f = need(mod, "open_ticket_titles")
    log = []
    with _client(log) as c:
        assert f(c, "web") == ["Login fails", "Crash on save", "Typo in footer", "Slow search"]
    assert len(log) == 3 and [e.get("cursor") for e in log] == [None, "c2", "c3"]
