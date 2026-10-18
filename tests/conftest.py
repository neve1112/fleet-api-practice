from datetime import datetime, timezone

import pytest

from app.main import create_app
from app.store import DeviceStore

FIXED_NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def store():
    return DeviceStore.from_seed(now=FIXED_NOW)


@pytest.fixture
def client(store):
    app = create_app(store=store, clock=lambda: FIXED_NOW)
    app.config["TESTING"] = True
    return app.test_client()
