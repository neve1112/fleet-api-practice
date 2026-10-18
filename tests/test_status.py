from datetime import timedelta

from app.status import device_status
from tests.conftest import FIXED_NOW


def ago(**kwargs):
    return FIXED_NOW - timedelta(**kwargs)


def test_recent_checkin_is_online():
    assert device_status(ago(seconds=30), FIXED_NOW) == "online"


def test_ten_minutes_silent_is_offline():
    assert device_status(ago(minutes=10), FIXED_NOW) == "offline"


def test_two_days_silent_is_offline():
    assert device_status(ago(days=2, seconds=60), FIXED_NOW) == "offline"


def test_nine_days_silent_is_dormant():
    assert device_status(ago(days=9), FIXED_NOW) == "dormant"


def test_never_seen_is_dormant():
    assert device_status(None, FIXED_NOW) == "dormant"
