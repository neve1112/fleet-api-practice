"""Fleet API: a tiny Meraki-dashboard-style service for device inventory."""
from datetime import datetime, timezone

from flask import Flask, abort, jsonify, request

from .status import device_status
from .store import DeviceStore


def serialize_device(device, now):
    return {
        "serial": device["serial"],
        "name": device["name"],
        "model": device["model"],
        "type": device["type"],
        "network_id": device["network_id"],
        "lan_ip": device["lan_ip"],
        "last_seen": device["last_seen"].isoformat() if device["last_seen"] else None,
        "status": device_status(device["last_seen"], now),
    }


def positive_int_arg(name, default):
    """Read a query param that must be an integer >= 1, or abort with a 400."""
    try:
        value = int(request.args.get(name, default))
    except ValueError:
        value = 0
    if value < 1:
        abort(400, description=f"'{name}' must be a positive integer")
    return value


def create_app(store=None, clock=None):
    app = Flask(__name__)
    store = store or DeviceStore.from_seed()
    clock = clock or (lambda: datetime.now(timezone.utc))

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": error.description}), 400

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/networks")
    def list_networks():
        return jsonify(store.networks())

    @app.get("/devices")
    def list_devices():
        page = positive_int_arg("page", 1)
        per_page = positive_int_arg("per_page", 10)
        devices = store.devices(network_id=request.args.get("network_id"))

        start = (page - 1) * per_page
        items = devices[start:start + per_page]

        now = clock()
        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": len(devices),
            "items": [serialize_device(d, now) for d in items],
        })

    @app.get("/devices/<serial>")
    def get_device(serial):
        device = store.get_device(serial)
        if device is None:
            abort(404)
        return serialize_device(device, clock())

    return app
