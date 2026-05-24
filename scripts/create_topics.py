import argparse
from concurrent.futures import TimeoutError

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topics", nargs="+", default=["frames", "processed_frames"])
    args = parser.parse_args()

    admin = AdminClient({"bootstrap.servers": args.bootstrap})
    new_topics = [NewTopic(name, num_partitions=1, replication_factor=1) for name in args.topics]
    futures = admin.create_topics(new_topics, request_timeout=15)

    for topic, future in futures.items():
        try:
            future.result(timeout=15)
            print(f"created topic {topic}")
        except TimeoutError:
            raise RuntimeError(f"timed out while creating topic {topic}") from None
        except KafkaException as exc:
            if "TOPIC_ALREADY_EXISTS" in str(exc):
                print(f"topic {topic} already exists")
            else:
                raise


if __name__ == "__main__":
    main()
