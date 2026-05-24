# Screenshots

Эта папка хранит evidence для ДЗ-8.

## Автоматически

```bash
cd DZ8
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
docker compose up -d
.venv/bin/python scripts/smoke_requests.py
.venv/bin/python scripts/take_screenshots.py
```

Ожидаемые файлы:

- `prometheus_targets_up.png` - Prometheus видит `ml_service` как `UP`
- `grafana_latency_panel.png` - dashboard `DZ-8 ML Service`
- `grafana_high_latency_alert.png` - alert list с `HighLatency`
- `dqops_incident.png` - DQOps UI; после ручного incident-flow заменить на screenshot Incidents page

## Как сделать руками

1. `docker compose up -d`
2. открыть `http://localhost:9090/targets`
3. проверить, что `ml_service` в состоянии `UP`
4. сохранить screenshot как `prometheus_targets_up.png`
5. открыть `http://localhost:3000/d/dz8-ml/dz-8-ml-service`
6. прогнать `.venv/bin/python scripts/smoke_requests.py`
7. сохранить dashboard screenshot как `grafana_latency_panel.png`
8. для alert:

```bash
for i in $(seq 1 30); do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features":[1,2,3],"slow":true}' >/dev/null
done
sleep 150
```

9. открыть `http://localhost:3000/alerting/list`
10. сохранить screenshot как `grafana_high_latency_alert.png`

## DQOps incident руками

1. открыть `http://localhost:8888`
2. Data sources -> Add connection -> PostgreSQL
3. параметры:

| field | value |
|---|---|
| host | `postgres` |
| port | `5432` |
| database | `dz8` |
| user | `dqops` |
| password | `dqops` |
| schema | `public` |
| table | `customer_orders` |

4. импортировать `customer_orders`
5. включить profiling/schema checks для таблицы или колонки `total_amount`
6. запустить checks один раз на нормальной таблице
7. применить mutation:

```bash
docker exec -i dz8_postgres psql -U dz8 -d dz8 < sql/break_orders_schema.sql
```

8. запустить checks снова
9. открыть Incidents и сохранить screenshot как `dqops_incident.png`

Сбросить БД после mutation:

```bash
docker compose down -v
docker compose up -d
```
