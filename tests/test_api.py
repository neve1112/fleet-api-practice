def test_health(client):
    assert client.get("/health").get_json() == {"ok": True}


def test_list_networks(client):
    ids = {n["id"] for n in client.get("/networks").get_json()}
    assert ids == {"N_SF_OFFICE", "N_NYC_BRANCH", "N_LON_STORE"}


def test_first_page_starts_at_first_device(client, store):
    body = client.get("/devices?page=1&per_page=5").get_json()
    expected = [d["serial"] for d in store.devices()[:5]]
    assert [d["serial"] for d in body["items"]] == expected


def test_paging_returns_every_device_exactly_once(client, store):
    seen = []
    page = 1
    while True:
        items = client.get(f"/devices?page={page}&per_page=10").get_json()["items"]
        if not items:
            break
        seen.extend(d["serial"] for d in items)
        page += 1
    assert sorted(seen) == sorted(d["serial"] for d in store.devices())


def test_filter_by_network(client):
    body = client.get("/devices?network_id=N_NYC_BRANCH&per_page=100").get_json()
    assert body["total"] > 0
    assert all(d["network_id"] == "N_NYC_BRANCH" for d in body["items"])


def test_get_device_by_serial(client, store):
    serial = store.devices()[0]["serial"]
    assert client.get(f"/devices/{serial}").get_json()["serial"] == serial


def test_get_device_serial_is_case_insensitive(client, store):
    serial = store.devices()[0]["serial"]
    resp = client.get(f"/devices/{serial.lower()}")
    assert resp.status_code == 200
    assert resp.get_json()["serial"] == serial


def test_unknown_device_is_404(client):
    assert client.get("/devices/Q2ZZ-0000-0000").status_code == 404
