import argparse
import json
import time

from confluent_kafka import Producer


def on_delivery(err, msg) -> None:
    if err is not None:
        print(f"delivery failed for key={msg.key()!r}: {err}")
        return
    print(
        "delivered to "
        f"{msg.topic()} partition {msg.partition()} offset {msg.offset()}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topic", default="frames")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    producer = Producer({"bootstrap.servers": args.bootstrap})
    countries = ["RU", "KZ", "AM", "GE", "TR"]
    slots = ["tshirt_logo", "billboard", "cup_label"]

    for frame_id in range(1, args.count + 1):
        event = {
            "frame_id": frame_id,
            "viewer_country": countries[frame_id % len(countries)],
            "brand_slot": slots[frame_id % len(slots)],
            "brand_candidate": "demo_brand",
            "model_version": "vpp-demo-v1",
        }
        producer.produce(
            args.topic,
            key=str(frame_id),
            value=json.dumps(event).encode("utf-8"),
            callback=on_delivery,
        )
        producer.poll(0)
        time.sleep(0.1)

    producer.flush(10)


if __name__ == "__main__":
    main()
