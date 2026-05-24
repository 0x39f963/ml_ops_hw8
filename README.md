# ДЗ-8 Monitoring / Observability

Минимальный воспроизводимый стенд для мониторинга ML-сервиса:

- FastAPI ML-service с `/health`, `/predict`, `/metrics`
- Prometheus target + alert rule `HighLatency`
- Grafana datasource/dashboard/alert provisioning
- Evidently drift/degradation reports
- PostgreSQL + DQOps incident workflow
- Virtual Product Placement Kappa diagram
- Redpanda Kafka-compatible stream demo

## 1. Как проверять по критериям

| критерий | максимум | где смотреть |
|---|---:|---|
| Бизнес- и технические метрики | 2 | ноутбук: раздел 1, README: `Метрики и SLO` |
| Prometheus / Grafana / ML monitoring | 2 | `app.py`, `prometheus.yml`, `grafana/provisioning/`, screenshots Prometheus/Grafana |
| Drift / degradation | 2 | `scripts/generate_drift_report.py`, `reports/data_drift_report.html`, `reports/degradation_metrics.json` |
| Data Quality Ops | 2 | `docker-compose.yml`, `sql/*.sql`, `screenshots/dqops_incident.png` |
| Virtual Product Placement | 2 | `reports/vpp_architecture.png`, `scripts/vpp_producer.py`, `scripts/vpp_consumer.py`, `reports/vpp_stream_demo.log` |

Итоговый ноутбук: `HW8_Monitoring_НовиковИван.ipynb`.

Что в нем сделано:

1. сначала идет дерево метрик / SLO
2. потом Prometheus + Grafana configs
3. дальше Evidently drift + degradation
4. отдельно DQOps incident через PostgreSQL
5. в конце VPP architecture + stream demo на Redpanda

Скриншоты уже лежат в `screenshots/`. Их можно переснять через `scripts/take_screenshots.py`, если надо обновить evidence после локального запуска.

## 2. Быстрый запуск

```bash
cd DZ8
docker compose up -d
docker compose ps
```

Порты:

| service | URL |
|---|---|
| ML service | `http://localhost:8000` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |
| DQOps | `http://localhost:8888` |
| Redpanda Kafka API | `localhost:9092` |
| PostgreSQL | `localhost:5432` |

Grafana anonymous access включен, dashboard уже импортирован:

```text
http://localhost:3000/d/dz8-ml/dz-8-ml-service
```

## 3. Python scripts

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

Для диаграммы нужен system Graphviz (`dot`). Если на машине нет `dot`, можно собрать PNG через Docker:

```bash
docker run --rm -v "$PWD":/work -w /work python:3.11-slim \
  sh -lc "apt-get update >/dev/null && apt-get install -y graphviz >/dev/null && pip install -q diagrams==0.23.4 && python scripts/create_vpp_diagram.py"
```

## 4. Проверки

Smoke:

```bash
.venv/bin/python scripts/smoke_requests.py
curl -s http://localhost:8000/metrics | grep request_latency_seconds_bucket
```

Prometheus target:

```bash
open http://localhost:9090/targets
```

Alert:

```bash
for i in $(seq 1 30); do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features":[1,2,3],"slow":true}' >/dev/null
done
sleep 150
open http://localhost:3000/alerting/list
```

Drift/degradation:

```bash
.venv/bin/python scripts/generate_drift_report.py
```

VPP stream demo:

```bash
.venv/bin/python scripts/create_topics.py
tmp_p=$(mktemp); tmp_c=$(mktemp)
.venv/bin/python scripts/vpp_consumer.py --count 10 > "$tmp_c" 2>&1 & pid=$!
sleep 3
.venv/bin/python scripts/vpp_producer.py --count 10 > "$tmp_p" 2>&1
wait $pid
{ echo '# producer'; cat "$tmp_p"; echo; echo '# consumer'; cat "$tmp_c"; } > reports/vpp_stream_demo.log
rm -f "$tmp_p" "$tmp_c"
```

Screenshots:

```bash
.venv/bin/python scripts/take_screenshots.py
```

## 5. Метрики и SLO

| branch | metric | SLI | SLO | owner | action |
|---|---|---|---|---|---|
| business | CTR/conversion | product KPI over window | no unexpected drop | product | analyze segment / pause rollout |
| application | p95 latency | PromQL p95 over 5m | `< 1 sec` | backend/MLOps | inspect latency / rollback slow model |
| application | error rate | failed requests ratio | `< 1%` | backend/MLOps | inspect logs / rollback |
| infrastructure | availability | `up{job="ml_service"}` | `> 99%` | DevOps | restart / failover |
| ML/model | drift PSI | Evidently PSI / drift share | `< 0.2` for PSI-style threshold | DS | validate data / retrain decision |
| ML/model | degradation | accuracy/F1 on labelled batch | not worse than baseline by agreed delta | DS | retrain / rollback |
| data quality | DQ incidents | DQOps critical incidents | `0 critical` | data engineer | fix source / backfill / isolate |

Основной alert в стенде:

```promql
histogram_quantile(0.95, sum(rate(request_latency_seconds_bucket[5m])) by (le)) > 1
```

## 6. Evidence

| block | artifact |
|---|---|
| FastAPI metrics | `app.py`, `/metrics`, `request_latency_seconds_bucket` |
| Prometheus | `prometheus.yml`, `alert_rules.yml`, `screenshots/prometheus_targets_up.png` |
| Grafana | `grafana/provisioning/**`, `screenshots/grafana_latency_panel.png`, `screenshots/grafana_high_latency_alert.png` |
| Drift | `reports/data_drift_report.html`, `reports/data_drift_tests.html` |
| Degradation | `reports/degradation_metrics.json` |
| DQOps | `docker-compose.yml`, `sql/init_orders.sql`, `sql/break_orders_schema.sql`, `screenshots/dqops_incident.png` |
| VPP architecture | `scripts/create_vpp_diagram.py`, `reports/vpp_architecture.png` |
| VPP stream | `scripts/vpp_producer.py`, `scripts/vpp_consumer.py`, `reports/vpp_stream_demo.log` |

## 7. Drift/degradation result

`scripts/generate_drift_report.py` использует `sklearn.datasets.load_wine`.

Текущий результат:

```json
{
  "baseline_acc": 0.9861,
  "current_acc": 0.5972,
  "delta": -0.3889
}
```

Data drift показывается без labels через Evidently. Degradation считается отдельно на labelled current batch: качество заметно падает после synthetic shift.

## 8. DQOps incident flow

В compose DQOps запинен на `dqops/dqo:1.10.1`. Причина: `dqops/dqo:latest` на момент проверки стартует как v1.13.1 и требует license key в headless-режиме, что ломает учебный `docker compose up -d` без секретов.

Проверка:

1. `docker compose up -d`
2. открыть `http://localhost:8888`
3. добавить PostgreSQL source:

| field | value |
|---|---|
| host | `postgres` |
| port | `5432` |
| db | `dz8` |
| user | `dqops` |
| pass | `dqops` |

4. импортировать `public.customer_orders`
5. включить profiling/schema checks
6. run checks
7. применить mutation:

```bash
docker exec -i dz8_postgres psql -U dz8 -d dz8 < sql/break_orders_schema.sql
```

8. run checks снова
9. открыть Incidents

После mutation колонка `total_amount` переименуется в `total_amount_broken`. Это controlled schema incident: контракт таблицы сломан, DQOps должен показать проблему после повторного check-run.

Сброс:

```bash
docker compose down -v
docker compose up -d
```

## 9. Virtual Product Placement

Выбрана Kappa architecture:

- входной video stream режется на кадры / micro-batches
- Kafka-compatible broker хранит event log
- detector + placement policy выбирают slot/brand
- generative renderer/inpainting вставляет бренд
- moderation / brand-safety gate блокирует плохие результаты
- processed frames topic идет в packager -> CDN/player
- Prometheus/Grafana + drift/DQ checks смотрят latency/lag/failures/input quality

Redpanda здесь не production video runtime. Это маленькое доказательство stream-подхода: producer пишет frame events в `frames`, consumer имитирует ML processing и пишет в `processed_frames`.

## 10. Что demo-only

- нет настоящего YOLO/video inference
- нет MLflow server, т.к. revised ТЗ убрало MLflow runtime из scope
- нет Redis/MinIO/Dagster/Feast
- нет Schema Registry / Avro / exactly-once
- DQOps incident требует ручной UI-flow, потому что это часть задания и UI-зависимая проверка

## 11. Teardown

```bash
docker compose down -v
```
