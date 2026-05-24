# Скриншоты

## Подготовка окружения

Подготовил Python-окружение:

Создал `.venv`, обновил `pip`, запустил установку зависимостей.

![создание окружения](1.png)

Пакеты/зависимости поставились. После этого запускаются проверка сервиса, drift,
диаграмма и стрим-демо.

![установка зависимостей](2.png)

## Запуск контейнеров

`docker compose up -d`

На скрине: все контейнеры - ML-сервис, Prometheus, Grafana, PostgreSQL, DQOps и
Redpanda.

![запущенные контейнеры](3.png)

## ML-сервис и метрики

Проверил FastAPI-сервис: `/health` отвечает, `/metrics` отдает метрики для
Prometheus.

На скрине видно `request_latency_seconds_bucket`. Это главная метрика для p95
latency.

![метрики сервиса](4.png)

Prometheus видит `ml_service` как `UP`, значит сбор `/metrics` работает.

![Prometheus видит сервис](5.png)

## Grafana и алерт

В Grafana открыт дашборд по ML-сервису: latency, частота запросов, статус
сервиса.

![дашборд Grafana](6.png)

Правила алертов тоже подтянулись из конфигов Grafana.

![правила алертов](7.png)

После медленных запросов в `/predict` алерт `HighLatency` перешел в `Firing`.
Так проверялось, что SLO по p95 latency реально контролируется, а не просто
записан в README.

![сработал HighLatency](8.png)

## Drift и degradation

Для drift я запустил скрипт:

```bash
.venv/bin/python scripts/generate_drift_report.py
```

Evidently показал, что часть drift-тестов упала. Это ожидаемо: current batch
специально смещен.

![тесты Evidently](10.png)

В отчете по drift видно, что drift detected и большая часть признаков уехала
относительно reference batch.

![отчет Evidently по drift](11.png)

Degradation отдельно сохранена в `reports/degradation_metrics.json`: там
качество модели на смещенном batch заметно ниже baseline.

## DQOps

В DQOps настроил проверку схемы для таблицы `customer_orders`.

![проверка схемы в DQOps](12.png)

Поломка схемы делается отдельным SQL:

```bash
docker exec -i dz8_postgres psql -U dz8 -d dz8 < sql/break_orders_schema.sql
```

Там колонка `total_amount` переименовывается в `total_amount_broken`. Это
пример контролируемого инцидента по качеству данных.

## Virtual Product Placement

Для VPP сделал не тяжелую видеообработку, а маленькую проверку стрим-подхода:

![схема VPP](../reports/vpp_architecture.png)

```text
producer -> frames -> consumer -> processed_frames
```

Пример обработанного события кадра:

![пример обработанного кадра](9.png)

Лог producer/consumer показывает, что события уходят в `frames`, а результат
пишется в `processed_frames`.

![лог стрим-демо](13.png)

Этим закрывается часть ДЗ про схему Virtual Product Placement со стримами:
Redpanda тут играет роль Kafka-compatible broker, а сама обработка оставлена
демо-уровня, чтобы не тащить реальное видео и тяжелые модели.
