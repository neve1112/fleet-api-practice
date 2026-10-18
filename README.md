# Fleet API

A small service that exposes network and device inventory for a cloud-managed
networking dashboard: appliances (MX), switches (MS), access points (MR) and
cameras (MV), grouped into networks.

## Run it

```bash
docker compose up --build api
```

The API should then answer on http://localhost:8080:

```bash
curl http://localhost:8080/health
curl "http://localhost:8080/devices?page=1&per_page=5"
```

## Test it

```bash
docker compose run --rm --build tests
```

## Endpoints

| Method | Path                | Notes                                              |
|--------|---------------------|----------------------------------------------------|
| GET    | `/health`           | Liveness check                                     |
| GET    | `/networks`         | All networks                                       |
| GET    | `/devices`          | Paginated. `page` (1-based), `per_page`, `network_id` |
| GET    | `/devices/<serial>` | One device, with computed `status`                 |

Device `status` is `online` (checked in within 5 min), `offline`, or
`dormant` (not seen for 7+ days, or never).

## Layout

```
app/main.py     Flask app and routes
app/store.py    In-memory store loaded from app/data/seed.json
app/status.py   Status calculation
tests/          pytest suite
```

Appliances (`type: appliance`) carry `uplink_samples`: the most recent WAN
measurements, oldest first, each with `loss_pct` and `latency_ms`.
