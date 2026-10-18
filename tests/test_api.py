import pytest


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


def test_mixed_case_serial_in_store_is_reachable():
    from app.store import DeviceStore
    device = {"serial": "Q2ab-Cd12-34Ef", "name": "x", "model": "MR46",
              "type": "wireless", "network_id": "N1", "lan_ip": "10.0.0.1",
              "last_seen": None}
    store = DeviceStore([{"id": "N1", "name": "n"}], [device])
    assert store.get_device("q2ab-cd12-34ef") is device
    assert store.get_device("Q2AB-CD12-34EF") is device


@pytest.mark.parametrize("query", [
    "page=abc", "page=0", "page=-1", "per_page=0", "per_page=xyz", "page=1.5",
])
def test_bad_paging_params_are_400_json(client, query):
    resp = client.get(f"/devices?{query}")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_mx_silent_since_tuesday_is_not_online():
    """Ticket 3: an MX that last checked in on Tuesday must not show as online."""
    from datetime import datetime, timezone
    from app.main import create_app
    from app.store import DeviceStore
    from tests.conftest import FIXED_NOW  # Thursday 2026-01-15 12:00 UTC

    tuesday = datetime(2026, 1, 13, 11, 59, 0, tzinfo=timezone.utc)  # 2 days + 60s ago
    mx = {"serial": "Q2MX-0000-0001", "name": "mx-branch", "model": "MX68",
          "type": "appliance", "network_id": "N1", "lan_ip": "10.0.0.1",
          "last_seen": tuesday}
    store = DeviceStore([{"id": "N1", "name": "n"}], [mx])
    client = create_app(store=store, clock=lambda: FIXED_NOW).test_client()

    body = client.get("/devices/Q2MX-0000-0001").get_json()
    assert body["status"] == "offline"
