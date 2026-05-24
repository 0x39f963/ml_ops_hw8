from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.blank import Blank
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.queue import Kafka


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    out = reports_dir / "vpp_architecture"

    graph_attr = {
        "fontsize": "18",
        "pad": "0.35",
        "ranksep": "0.7",
        "nodesep": "0.45",
    }

    with Diagram(
        "DZ8 Virtual Product Placement Kappa Architecture",
        filename=str(out),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=graph_attr,
    ):
        source = Blank("video source")
        splitter = Blank("frame splitter")

        with Cluster("Kappa stream layer"):
            broker = Kafka("frames topic / event log")
            processed = Kafka("processed_frames topic")

        with Cluster("ML processing"):
            detector = Blank("detector + placement policy")
            renderer = Blank("generative renderer / inpainting")
            moderation = Blank("moderation / brand-safety gate")

        packager = Blank("stream packager -> CDN/player")

        with Cluster("Observability"):
            prometheus = Prometheus("Prometheus")
            grafana = Grafana("Grafana alerts")
            checks = Blank("drift / DQ checks")

        source >> splitter >> broker
        broker >> detector >> renderer >> moderation >> processed >> packager
        [splitter, detector, renderer, moderation, packager] >> Edge(label="/metrics") >> prometheus >> grafana
        broker >> Edge(label="replay / lag") >> checks
        processed >> Edge(label="quality windows") >> checks

    print(f"saved {out.with_suffix('.png')}")


if __name__ == "__main__":
    main()
