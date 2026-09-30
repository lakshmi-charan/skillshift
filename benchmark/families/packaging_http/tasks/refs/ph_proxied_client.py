import httpx


def make_proxied_client(proxy_url, base_url):
    return httpx.Client(base_url=base_url, proxy=proxy_url, timeout=5.0,
                        headers={"User-Agent": "inventory-sync/1.0"})
