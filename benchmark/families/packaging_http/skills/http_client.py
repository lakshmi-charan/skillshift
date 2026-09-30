"""httpx client factory for calls to our internal services (written against httpx 0.27)."""
import httpx

DEFAULT_TIMEOUT = 10.0


def _raise_on_error(response):
    response.raise_for_status()


def make_client(base_url="", *, headers=None, timeout=DEFAULT_TIMEOUT, proxy_url=None,
                raise_errors=False, transport=None):
    """Create an httpx.Client.

    proxy_url     -- route every request through this HTTP proxy (e.g. "http://proxy.corp:3128")
    raise_errors  -- raise httpx.HTTPStatusError for 4xx/5xx responses
    transport     -- custom transport (tests pass httpx.MockTransport)
    """
    kwargs = {}
    if proxy_url:
        kwargs["proxies"] = proxy_url
    hooks = {"response": [_raise_on_error]} if raise_errors else {}
    return httpx.Client(base_url=base_url, headers=headers, timeout=timeout, transport=transport,
                        event_hooks=hooks, **kwargs)


def make_wsgi_client(app, base_url="http://testserver", headers=None):
    """Client that calls a WSGI application in-process (no network), for integration tests."""
    return httpx.Client(app=app, base_url=base_url, headers=headers)
