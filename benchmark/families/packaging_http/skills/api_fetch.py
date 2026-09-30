"""Helpers for JSON REST APIs on top of an httpx.Client."""


class ApiError(Exception):
    def __init__(self, status_code, body):
        super().__init__("API request failed with status %d" % status_code)
        self.status_code = status_code
        self.body = body


RETRY_STATUSES = (502, 503, 504)


def _check(response):
    if response.is_error:
        raise ApiError(response.status_code, response.text)
    return response


def fetch_json(client, path, params=None, retries=2):
    """GET `path` (which may already carry a query string) with extra query `params`.
    Retries on 502/503/504; raises ApiError for other error statuses; returns the decoded JSON."""
    for attempt in range(retries + 1):
        response = client.get(path, params=params)
        if response.status_code in RETRY_STATUSES and attempt < retries:
            continue
        return _check(response).json()


def post_json(client, path, payload):
    """POST `payload` as a JSON body and return the decoded JSON response."""
    return _check(client.post(path, json=payload)).json()


def iter_items(client, path, params=None, max_pages=100):
    """Yield the items of a paginated endpoint returning {"items": [...], "next": <url or null>}.
    `params` (filters) are sent with every page request."""
    url = path
    for _ in range(max_pages):
        data = fetch_json(client, url, params=params)
        for item in data["items"]:
            yield item
        url = data.get("next")
        if not url:
            return
