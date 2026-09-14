# Week 03 Lab

Build an ingestion pipeline from a public API/dataset; handle errors and retries.

Starter files for this week's lab will be added here before the lab session
(pulled into your repo via `git fetch upstream && git merge upstream/main`,
as introduced in the Week 1 lab).

## Reflection

The timeout and connection error were both easiest to trigger — each is a single-line, purely mechanical edit (drop `timeout` to 0.001, or point `url` at a domain that doesn't exist) with no knowledge of the API itself required. The HTTP 400 was hardest, since triggering it on purpose meant actually knowing the API's valid input range (latitude must be -90 to 90) rather than just breaking the network layer.

Exponential backoff visibly stretched the timing between attempts: the printed delays grew 1s → 2s → 4s across the three retries before giving up on the fourth attempt, versus failing instantly with no retry logic at all. That's roughly 7 extra seconds of total wait before the script gives up, all spent giving a transient glitch a chance to clear on its own.

We deliberately don't retry the HTTP 400 because it's not transient — an invalid latitude will fail exactly the same way on every attempt, so retrying it wastes time and API load for zero chance of success. This connects directly to the lecture's point about retry storms: if many ingestion jobs all retried a permanently broken request against an already-struggling API, the retries themselves pile on load and can turn a minor outage into a much bigger one.

For a data contract on `data/raw/`, I'd want to specify: **schema** (the exact JSON shape — `latitude`, `longitude`, `current_units`, and a `current` object with `time`, `temperature_2m`, `wind_speed_10m`, `relative_humidity_2m`); **semantics** (units come from `current_units`, `current.time` is local per the API's auto-detected `timezone`, and — something we actually hit ourselves — a landed file can contain a bare `null` when a fetch failed, so consumers need to explicitly handle that case rather than assume every file is a valid payload); **SLA** (how often each city is expected to land, and what a missing/skipped city in a given run means); and **change management** (advance notice before adding/renaming fields, changing the filename format, or adding/removing cities, so a consumer's parser doesn't silently break on the next ingestion run).
