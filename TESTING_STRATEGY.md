# Testing Strategy OPEN FNR

## 1. Назначение

Документ описывает стратегию тестирования OPEN FNR: data, ML, backend, process engine, UI, integrations, performance, security и acceptance.

## 2. Принципы

- тестирование начинается с данных;
- бизнес-процессы тестируются end-to-end;
- ML тестируется через backtesting и monitoring;
- UI тестируется по бизнес-процессам;
- performance gates обязательны;
- regression suite запускается на CI;
- production releases проходят stage rehearsal.

## 3. Уровни Тестирования

| Уровень | Что тестируется |
| --- | --- |
| Unit | функции, правила, валидаторы |
| Component | сервисы и модули |
| Integration | API, DB, ERP/WMS mocks |
| Data Quality | полнота, дубли, справочники |
| ML Validation | backtesting, WAPE, Bias |
| Process Tests | BPMN/DMN/CMMN paths |
| UI E2E | бизнес-сценарии |
| Performance | SLA, load, stress |
| Security | RBAC, audit, secrets |
| UAT | бизнес-приемка |

## 4. Data Testing

Проверяются:

- schema;
- nulls;
- duplicates;
- referential integrity;
- freshness;
- row counts;
- price anomalies;
- stock anomalies;
- promo completeness.

## 5. ML Testing

Проверяются:

- baseline comparison;
- rolling backtesting;
- category-level metrics;
- promo uplift accuracy;
- fresh metrics;
- inference performance;
- reproducibility;
- fallback scenarios.

## 6. Backend/API Testing

Проверяются:

- OpenAPI contracts;
- authentication;
- authorization;
- pagination;
- filtering;
- idempotency;
- error schema;
- audit logs;
- version compatibility.

## 7. Process Engine Testing

Проверяются:

- BPMN happy paths;
- BPMN exception paths;
- DMN decision tables;
- CMMN lifecycle;
- process migration;
- process rollback;
- task assignment;
- SLA timers.

## 8. UI Testing

UI-тестирование описано отдельно в [UI_TESTING_SPEC.md](UI_TESTING_SPEC.md).

Обязательные направления:

- smoke;
- E2E;
- validation;
- RBAC;
- audit;
- visual regression;
- performance UI.

## 9. Integration Testing

Проверяются:

- POS inbound;
- ERP inbound/outbound;
- WMS inbound/outbound;
- DWH exports;
- MDM snapshots;
- promo import;
- retry;
- idempotency;
- reject handling.

## 10. Performance Testing

Проверяются:

- feature engineering runtime;
- inference runtime;
- replenishment runtime;
- ClickHouse write/read;
- API latency;
- UI latency;
- export throughput;
- failure recovery.

## 11. Acceptance Testing

Приемка выполняется по:

- business process criteria;
- KPI criteria;
- SLA criteria;
- integration criteria;
- security criteria;
- support readiness.

## 12. CI/CD Gates

Релиз не проходит, если:

- unit tests failed;
- API contract tests failed;
- critical DQ tests failed;
- ML metrics below threshold;
- BPMN/DMN tests failed;
- UI smoke failed;
- security checks failed;
- performance baseline degraded.

## 13. Test Environments

| Среда | Назначение |
| --- | --- |
| DEV | разработка |
| TEST | automated tests |
| STAGE | production-like rehearsal |
| PROD | production |

## 14. Критерии Приемки

- test matrix покрывает ключевые процессы;
- CI запускает regression;
- UI E2E покрывает BP-01 - BP-20;
- performance tests подтверждают SLA;
- UAT завершен;
- defects triaged;
- release decision documented.
# Правило HTML-Отчётов

Для каждого значимого тестового цикла формируется HTML-отчёт в `docs/test-reports`.

Минимальный состав отчёта:

- аннотация: что и для чего тестируется;
- UI-сценарии по шагам с ожидаемым и фактическим результатом;
- бизнес-процессы по шагам с BPMN/DMN/CMMN контекстом;
- результаты backend/data/process/security/performance проверок, если применимо;
- скриншоты UI;
- вывод и известные ограничения.

## Правило Блоковых Презентаций

После завершения крупного блока спринтов дополнительно к тестовым отчётам формируется HTML-презентация для двух аудиторий:

- пользователи: бизнес-сценарии, экраны, роли, результаты, ограничения;
- разработчики: структура модуля, API, данные, BPMN/DMN/CMMN, тесты, точки расширения.

Презентация должна опираться на реальные скриншоты из UI и ссылки на тестовые отчёты. Формат хранения:

`docs/presentations/<block-name>/index.html`.

В презентации обязательно раскрываются:

- назначение модуля;
- покрываемые бизнес-процессы;
- структура реализации;
- пользовательские сценарии;
- процессные сценарии;
- результаты тестирования;
- риски и следующий план работ.
