# Mock live round: Fleet API

**Time box: 60 minutes.** Talk out loud the whole time, as if the panel were
watching your screen. Use your AI tool as you would in the real round, but
read and own everything it produces.

Work through the tickets in order. Commit after each one with a clear message.

---

### Ticket 1: "The service doesn't come up" (about 5 min)

> A new teammate ran `docker compose up --build api`. The container starts and
> the logs look healthy, but `curl http://localhost:8080/health` from the host
> fails to connect.

Make the service reachable from the host.

---

### Ticket 2: "CI is red" (about 15 min)

> `docker compose run --rm --build tests` has failures.

Get the suite green **by fixing the code, not the tests**. For each failure,
be ready to explain the root cause in one sentence.

---

### Ticket 3: Customer escalation (about 5 min)

> A support engineer says: "A customer's MX hasn't checked in since Tuesday,
> but the dashboard shows it as **online**."

Is this covered by what you fixed already? Prove it with a test that reproduces
the customer's report exactly.

---

### Ticket 4: New endpoint, uplink health (about 25 min)

Product wants a WAN health view per network:

```
GET /networks/<network_id>/uplink-health?window=5
```

- `window`: how many of the **most recent** samples to use. Default `5`.
  Must be an integer from 1 to 12; anything else is a `400` with a JSON error.
- Unknown network: `404`.
- Include only devices that have uplink samples.
- Per device return `serial`, `name`, `avg_loss_pct`, `avg_latency_ms`
  (rounded to 2 dp) and `degraded`: true when average loss is above 2% **or**
  average latency is above 150 ms.
- Sort worst first: degraded devices first, then by `avg_loss_pct` descending.

Write tests for it, including the edge cases.

---

### Ticket 5: Discussion (remaining time)

Be ready to talk through, without necessarily coding:

1. `GET /devices?page=abc` today returns a 500. What should it return, and how
   would you handle bad query params across the API consistently?
2. This store is in memory. What changes when the inventory is 2 million devices
   across 50k networks, and the dashboard polls `/devices` every 10 seconds?
3. Devices check in over an unreliable link. How would you avoid a device
   flapping between online and offline on the dashboard?
4. Where did your AI tool help, and where did you have to correct it?
