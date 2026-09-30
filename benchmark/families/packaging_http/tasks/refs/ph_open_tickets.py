import httpx


def open_ticket_titles(client, project):
    filters = {"status": "open", "project": project}
    titles = []
    url = "/tickets"
    while url:
        resp = client.get(httpx.URL(url).copy_merge_params(filters))
        resp.raise_for_status()
        data = resp.json()
        titles.extend(item["title"] for item in data["items"])
        url = data.get("next")
    return titles
