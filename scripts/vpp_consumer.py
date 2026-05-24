import argparse
import json
import random
import time

from confluent_kafka import Consumer, Producer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--input-topic", default="frames")
    parser.add_argument("--output-topic", default="processed_frames")
    parser.add_argument("--group-id", default=f"dz8-vpp-demo-{int(time.time())}")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--timeout-sec", type=int, default=60)
    parser.add_argument("--offset-reset", default="latest", choices=["earliest", "latest"])
    args = parser.parse_args()

    consumer = Consumer(
        {
            "bootstrap.servers": args.bootstrap,
            "group.id": args.group_id,
            "auto.offset.reset": args.offset_reset,
            "enable.auto.commit": True,
        }
    )
    producer = Producer({"bootstrap.servers": args.bootstrap})
    consumer.subscribe([args.input_topic])

    processed = 0
    deadline = time.time() + args.timeout_sec
    try:
        while processed < args.count and time.time() < deadline:
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                print(f"consumer error: {msg.error()}")
                continue

            event = json.loads(msg.value().decode("utf-8"))
            started = time.perf_counter()
            time.sleep(random.uniform(0.02, 0.08))
            latency_ms = int((time.perf_counter() - started) * 1000)
            result = {
                "frame_id": event["frame_id"],
                "status": "processed",
                "brand_inserted": event["brand_candidate"],
                "latency_ms": latency_ms,
            }
            producer.produce(
                args.output_topic,
                key=str(event["frame_id"]),
                value=json.dumps(result).encode("utf-8"),
            )
            producer.poll(0)
            producer.flush(5)
            processed += 1
            print(
                f"processed frame_id={event['frame_id']} -> "
                f"{args.output_topic}: {json.dumps(result, ensure_ascii=False)}",
                flush=True,
            )
    finally:
        consumer.close()

    if processed < args.count:
        raise RuntimeError(f"processed only {processed}/{args.count} events")


if __name__ == "__main__":
    main()
