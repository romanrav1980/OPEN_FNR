# OPEN FNR Dev Infrastructure

Локальный dev-контур поднимается через Docker Compose / `nerdctl compose` и не требует Docker Desktop как обязательной зависимости.

## Сервисы

| Сервис | URL / порт | Назначение |
| --- | --- | --- |
| PostgreSQL | `localhost:15432` | metadata, process DB, API DB |
| ClickHouse HTTP | `http://localhost:18123` | forecast/replenishment store |
| ClickHouse native | `localhost:19000` | native client |
| Flowable REST | `http://localhost:18080` | BPMN/DMN/CMMN process engine |
| Airflow | `http://localhost:18088` | batch orchestration |
| OpenSearch | `http://localhost:19200` | logs/search |
| OpenSearch Dashboards | `http://localhost:15601` | logs UI |
| Superset | `http://localhost:18089` | BI dashboards |

## Учетные Записи Dev

| Сервис | Логин | Пароль |
| --- | --- | --- |
| Airflow | `admin` | `admin` |
| Superset | `admin` | `admin` |
| Flowable REST | `rest-admin` | `test` |
| PostgreSQL | `open_fnr` | `open_fnr_dev` |
| ClickHouse | `open_fnr` | `open_fnr_dev` |

Для проверки Airflow health на Windows лучше использовать `127.0.0.1`, а не `localhost`:

```powershell
curl.exe http://127.0.0.1:18088/health
```

## Запуск

```powershell
Copy-Item infra/dev/.env.example infra/dev/.env
docker compose --env-file infra/dev/.env -f infra/dev/compose.yaml up -d
```

## Проверка

```powershell
docker compose --env-file infra/dev/.env -f infra/dev/compose.yaml ps
```

## Остановка

```powershell
docker compose --env-file infra/dev/.env -f infra/dev/compose.yaml down
```

## Очистка Данных

```powershell
docker compose --env-file infra/dev/.env -f infra/dev/compose.yaml down -v
```
