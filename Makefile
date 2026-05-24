PYTHON ?= python3

.PHONY: up smoke drift diagram topics stream-demo screenshots compile down

up:
	docker compose up -d

smoke:
	$(PYTHON) scripts/smoke_requests.py

drift:
	$(PYTHON) scripts/generate_drift_report.py

diagram:
	$(PYTHON) scripts/create_vpp_diagram.py

topics:
	$(PYTHON) scripts/create_topics.py

stream-demo:
	$(PYTHON) scripts/create_topics.py
	rm -f reports/vpp_stream_demo.log
	$(PYTHON) scripts/vpp_consumer.py --count 10 > reports/vpp_stream_demo.log 2>&1 & pid=$$!; \
	sleep 2; \
	$(PYTHON) scripts/vpp_producer.py --count 10; \
	wait $$pid; \
	cat reports/vpp_stream_demo.log

screenshots:
	$(PYTHON) scripts/take_screenshots.py

compile:
	$(PYTHON) -m compileall -q app.py scripts

down:
	docker compose down -v
