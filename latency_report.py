import csv
import statistics
from pathlib import Path


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    lower = int(k)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    weight = k - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def main() -> None:
    path = Path("latency_log.csv")
    if not path.exists():
        print("latency_log.csv not found")
        return

    e2e = []
    transport = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            e2e.append(float(row["end_to_end_ms"]))
            transport.append(float(row["transport_ms"]))

    if not e2e:
        print("No latency records available.")
        return

    print(f"samples: {len(e2e)}")
    print(f"e2e median: {statistics.median(e2e):.2f} ms")
    print(f"e2e p95: {percentile(e2e, 0.95):.2f} ms")
    print(f"transport median: {statistics.median(transport):.2f} ms")
    print(f"transport p95: {percentile(transport, 0.95):.2f} ms")


if __name__ == "__main__":
    main()
