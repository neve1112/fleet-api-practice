"""Device connectivity status, derived from when the cloud last heard from it."""

ONLINE_THRESHOLD_SECONDS = 5 * 60            # checked in within 5 minutes
DORMANT_THRESHOLD_SECONDS = 7 * 24 * 60 * 60  # not seen for a week or more


def device_status(last_seen, now):
    """Return one of: "online", "offline", "dormant"."""
    if last_seen is None:
        return "dormant"
    elapsed = (now - last_seen).total_seconds()
    if elapsed <= ONLINE_THRESHOLD_SECONDS:
        return "online"
    if elapsed < DORMANT_THRESHOLD_SECONDS:
        return "offline"
    return "dormant"
