import argparse
from pathlib import Path

from playwright.sync_api import Error, TimeoutError, sync_playwright


TARGETS = [
    (
        "prometheus_targets_up",
        "http://localhost:9090/targets",
        "Prometheus targets page. Expected: ml_service target is UP.",
        "networkidle",
    ),
    (
        "grafana_latency_panel",
        "http://localhost:3000/d/dz8-ml/dz-8-ml-service?orgId=1&from=now-30m&to=now&kiosk",
        "Grafana dashboard. Expected: p95 latency panel is visible.",
        "networkidle",
    ),
    (
        "grafana_high_latency_alert",
        "http://localhost:3000/alerting/list?orgId=1",
        "Grafana alert list. Expected: HighLatency is Normal/Pending/Firing after slow traffic.",
        "networkidle",
    ),
    (
        "dqops_incident",
        "http://localhost:8888",
        "DQOps page. Expected after manual setup: Incidents page with schema incident.",
        "domcontentloaded",
    ),
]


def fallback_page(page, title: str, message: str) -> None:
    page.set_content(
        f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 40px; background: #f6f7fb;">
            <h1>{title}</h1>
            <p style="font-size: 18px; max-width: 880px;">{message}</p>
            <p>Manual fallback steps are documented in screenshots/README.md.</p>
          </body>
        </html>
        """
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="screenshots")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for name, url, note, wait_until in TARGETS:
            path = out_dir / f"{name}.png"
            try:
                page.goto(url, wait_until=wait_until, timeout=args.timeout_ms)
                page.wait_for_timeout(8000 if name == "dqops_incident" else 1500)
            except (Error, TimeoutError) as exc:
                fallback_page(
                    page,
                    f"{name}: manual screenshot needed",
                    f"Could not open {url}. {note} Error: {exc}",
                )
            page.screenshot(path=str(path), full_page=True)
            print(f"saved {path}")
        browser.close()


if __name__ == "__main__":
    main()
