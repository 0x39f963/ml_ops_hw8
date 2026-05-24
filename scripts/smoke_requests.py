import argparse
import json
import time

import requests


def post_predict(base_url: str, features: list[float], slow: bool) -> float:
    started = time.perf_counter()
    resp = requests.post(
        f"{base_url}/predict",
        json={"features": features, "slow": slow},
        timeout=10,
    )
    resp.raise_for_status()
    return time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--fast", type=int, default=20)
    parser.add_argument("--slow", type=int, default=10)
    args = parser.parse_args()

    health = requests.get(f"{args.base_url}/health", timeout=5)
    health.raise_for_status()

    fast_times = []
    slow_times = []
    for _ in range(args.fast):
        fast_times.append(post_predict(args.base_url, [1, 2, 3], slow=False))
    for _ in range(args.slow):
        slow_times.append(post_predict(args.base_url, [1, 2, 3], slow=True))

    metrics = requests.get(f"{args.base_url}/metrics", timeout=5)
    metrics.raise_for_status()
    if "request_latency_seconds_bucket" not in metrics.text:
        raise RuntimeError("request_latency_seconds_bucket was not found in /metrics")

    result = {
        "health": health.json(),
        "fast_requests": args.fast,
        "slow_requests": args.slow,
        "fast_max_sec": round(max(fast_times), 4) if fast_times else None,
        "slow_max_sec": round(max(slow_times), 4) if slow_times else None,
        "metric_found": "request_latency_seconds_bucket",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
