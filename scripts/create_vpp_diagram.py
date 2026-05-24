from pathlib import Path
from shutil import which

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.blank import Blank
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.queue import Kafka


def render_with_diagrams(out: Path) -> None:
    graph_attr = {
        "fontsize": "18",
        "pad": "0.45",
        "ranksep": "1.0",
        "nodesep": "0.65",
        "splines": "ortho",
    }
    edge_attr = {"color": "#6f7f8f", "arrowsize": "0.75", "penwidth": "1.2"}

    with Diagram(
        "DZ8 VPP Kappa Architecture",
        filename=str(out),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=graph_attr,
        edge_attr=edge_attr,
    ):
        source = Blank("video\nsource")
        splitter = Blank("frame\nsplitter")

        with Cluster("Kappa stream layer"):
            broker = Kafka("frames\n/event log")
            processed = Kafka("processed\nframes")

        with Cluster("ML processing"):
            detector = Blank("detector\n+ policy")
            renderer = Blank("renderer\n/inpainting")
            moderation = Blank("brand-safety\ngate")

        packager = Blank("packager\nCDN/player")

        with Cluster("Observability"):
            prometheus = Prometheus("Prometheus")
            grafana = Grafana("Grafana\nalerts")
            checks = Blank("drift / DQ\nchecks")

        source >> splitter >> broker
        broker >> detector >> renderer >> moderation >> processed >> packager
        broker >> Edge(label="replay / lag", style="dashed") >> checks
        processed >> Edge(label="quality windows", style="dashed") >> checks
        packager >> Edge(label="/metrics", style="dashed") >> prometheus >> grafana
        checks >> Edge(label="checks", style="dashed") >> prometheus


def render_fallback_png(out_png: Path) -> None:
    # Запасной рендер нужен для запуска без системного graphviz/dot.
    from playwright.sync_api import sync_playwright

    html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  body { margin: 0; background: #ffffff; font-family: Arial, sans-serif; }
  svg { display: block; width: 1600px; height: 760px; }
  .box { fill: #eef7fb; stroke: #8da3b3; stroke-width: 1.4; rx: 12; }
  .group { fill: #f8fcff; stroke: #a9bbc8; stroke-width: 1.2; rx: 16; }
  .accent { fill: #e7f3ff; stroke: #6d91b5; stroke-width: 1.4; rx: 12; }
  .obs { fill: #fff8e7; stroke: #c8a45d; stroke-width: 1.4; rx: 12; }
  .text { fill: #263238; font-size: 18px; }
  .small { fill: #455a64; font-size: 15px; }
  .title { fill: #263238; font-size: 28px; font-weight: 600; }
  .edge { stroke: #6f7f8f; stroke-width: 2; fill: none; marker-end: url(#arrow); }
  .dash { stroke: #6f7f8f; stroke-width: 1.8; fill: none; stroke-dasharray: 8 7; marker-end: url(#arrow); }
</style>
</head>
<body>
<svg id="diagram" viewBox="0 0 1600 760" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#6f7f8f"/>
    </marker>
  </defs>

  <text x="800" y="58" text-anchor="middle" class="title">Virtual Product Placement: Kappa stream architecture</text>

  <text x="490" y="128" text-anchor="middle" class="small">Kappa stream layer</text>
  <text x="905" y="128" text-anchor="middle" class="small">ML processing</text>
  <text x="850" y="470" text-anchor="middle" class="small">Observability</text>

  <rect x="40" y="215" width="150" height="86" class="box"/>
  <text x="115" y="251" text-anchor="middle" class="text">video</text>
  <text x="115" y="275" text-anchor="middle" class="text">source</text>

  <rect x="230" y="215" width="160" height="86" class="box"/>
  <text x="310" y="251" text-anchor="middle" class="text">frame</text>
  <text x="310" y="275" text-anchor="middle" class="text">splitter</text>

  <rect x="430" y="205" width="180" height="106" class="accent"/>
  <text x="520" y="246" text-anchor="middle" class="text">frames</text>
  <text x="520" y="270" text-anchor="middle" class="small">topic / event log</text>

  <rect x="660" y="205" width="160" height="106" class="box"/>
  <text x="740" y="246" text-anchor="middle" class="text">detector</text>
  <text x="740" y="270" text-anchor="middle" class="small">+ policy</text>

  <rect x="860" y="205" width="160" height="106" class="box"/>
  <text x="940" y="246" text-anchor="middle" class="text">renderer</text>
  <text x="940" y="270" text-anchor="middle" class="small">inpainting</text>

  <rect x="1060" y="205" width="180" height="106" class="box"/>
  <text x="1150" y="246" text-anchor="middle" class="text">brand-safety</text>
  <text x="1150" y="270" text-anchor="middle" class="small">moderation gate</text>

  <rect x="1280" y="205" width="190" height="106" class="accent"/>
  <text x="1375" y="246" text-anchor="middle" class="text">processed</text>
  <text x="1375" y="270" text-anchor="middle" class="small">frames topic</text>

  <rect x="1280" y="365" width="190" height="86" class="box"/>
  <text x="1375" y="399" text-anchor="middle" class="text">stream packager</text>
  <text x="1375" y="423" text-anchor="middle" class="small">CDN / player</text>

  <rect x="475" y="535" width="180" height="82" class="obs"/>
  <text x="565" y="582" text-anchor="middle" class="text">drift / DQ checks</text>

  <rect x="745" y="535" width="180" height="82" class="obs"/>
  <text x="835" y="570" text-anchor="middle" class="text">Prometheus</text>
  <text x="835" y="594" text-anchor="middle" class="small">/metrics</text>

  <rect x="1015" y="535" width="180" height="82" class="obs"/>
  <text x="1105" y="570" text-anchor="middle" class="text">Grafana</text>
  <text x="1105" y="594" text-anchor="middle" class="small">alerts</text>

  <path class="edge" d="M190 258 H230"/>
  <path class="edge" d="M390 258 H430"/>
  <path class="edge" d="M610 258 H660"/>
  <path class="edge" d="M820 258 H860"/>
  <path class="edge" d="M1020 258 H1060"/>
  <path class="edge" d="M1240 258 H1280"/>
  <path class="edge" d="M1375 311 V365"/>

  <path class="dash" d="M520 311 V535"/>
  <text x="536" y="422" class="small">replay / lag</text>

  <path class="dash" d="M1375 311 V500 H610 V535"/>
  <text x="1100" y="486" class="small">quality windows</text>

  <path class="dash" d="M1375 451 V500 H835 V535"/>
  <text x="1090" y="523" class="small">/metrics</text>

  <path class="edge" d="M655 576 H745"/>
  <path class="edge" d="M925 576 H1015"/>

  <text x="800" y="700" text-anchor="middle" class="small">
    frames -> ML processing -> processed_frames; checks and metrics go to Prometheus/Grafana
  </text>
</svg>
</body>
</html>
"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 760}, device_scale_factor=1)
        page.set_content(html)
        page.locator("#diagram").screenshot(path=str(out_png))
        browser.close()


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    out = reports_dir / "vpp_architecture"

    if which("dot"):
        render_with_diagrams(out)
    else:
        render_fallback_png(out.with_suffix(".png"))

    print(f"saved {out.with_suffix('.png')}")


if __name__ == "__main__":
    main()
