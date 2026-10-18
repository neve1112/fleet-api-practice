"""In-memory store for networks and devices, loaded from a JSON seed file."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED_PATH = Path(__file__).parent / "data" / "seed.json"


class DeviceStore:
    def __init__(self, networks, devices):
        self._networks = {n["id"]: n for n in networks}
        self._devices = {d["serial"]: d for d in devices}

    @classmethod
    def from_seed(cls, path=SEED_PATH, now=None):
        """Load the seed file. `last_seen_seconds_ago` is converted to an
        absolute UTC timestamp relative to `now` so the demo data stays fresh."""
        now = now or datetime.now(timezone.utc)
        raw = json.loads(Path(path).read_text())
        devices = []
        for d in raw["devices"]:
            d = dict(d)
            ago = d.pop("last_seen_seconds_ago")
            d["last_seen"] = None if ago is None else now - timedelta(seconds=ago)
            devices.append(d)
        return cls(raw["networks"], devices)

    def networks(self):
        return list(self._networks.values())

    def get_network(self, network_id):
        return self._networks.get(network_id)

    def devices(self, network_id=None):
        """All devices, sorted by serial, optionally filtered by network."""
        items = sorted(self._devices.values(), key=lambda d: d["serial"])
        if network_id:
            items = [d for d in items if d["network_id"] == network_id]
        return items

    def get_device(self, serial):
        return self._devices.get(serial)
