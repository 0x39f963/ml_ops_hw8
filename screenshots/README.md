# Screenshots

Скриншоты для ДЗ-8 лежат тут же, `screenshots/1.png` - `screenshots/13.png`.

Короткая карта:

| file | что видно |
|---|---|
| `1.png` | создание `.venv`, установка зависимостей начинается |
| `2.png` | зависимости установлены успешно |
| `3.png` | `docker compose ps`, все сервисы подняты |
| `4.png` | `/health`, `/metrics`, `request_latency_seconds_bucket` |
| `5.png` | Prometheus target `ml_service` в `UP` |
| `6.png` | Grafana dashboard с latency / request rate / target up |
| `7.png` | Grafana alert rules, provisioned rules |
| `8.png` | `HighLatency` в состоянии `Firing` |
| `9.png` | demo processed frame для VPP |
| `10.png` | Evidently drift tests |
| `11.png` | Evidently dataset drift report |
| `12.png` | DQOps schema monitoring check |
| `13.png` | VPP producer/consumer log через Redpanda topics |

В README используются все эти скрины, но основные evidence:

- monitoring: `4.png`, `5.png`, `6.png`, `7.png`, `8.png`
- drift: `10.png`, `11.png`
- DQOps: `12.png`
- VPP stream: `9.png`, `13.png`
