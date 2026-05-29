# План Внедрения Process Navigator

Status: active implementation plan
Date: 2026-05-29
Source specs:

- [PROCESS_NAVIGATOR_MAP_SPEC.md](PROCESS_NAVIGATOR_MAP_SPEC.md)
- [PROCESS_NAVIGATOR_MAP_SPEC_SUPPLEMENT_1.md](PROCESS_NAVIGATOR_MAP_SPEC_SUPPLEMENT_1.md)
- [SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md](SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md)

## 1. Назначение

Документ фиксирует тактический план реализации Process Navigator после расширения спецификации Supplement 1. План принимает изменения соседнего агента как корректные: async conformance, performance SLA, lazy loading, real-time refresh, RBAC, business key tracking, alert deduplication и v2 boundaries.

## 2. Принципы Реализации

| Принцип | Требование |
| --- | --- |
| Config first | Environment, intervals, TTL, pagination, thresholds и network settings берутся из `config.py`, `.env.example` и frontend config |
| Backend contract first | Каждый UI-слой реализуется после стабильного API contract и backend tests |
| BPMN boundary | BPMN runtime artifacts находятся в `processes/`; DMN/CMMN остаются governed API artifacts до отдельного adapter approval |
| Lazy loading | `zoom=0` не загружает conformance, performance, versions и infrastructure details |
| Help-first UI | Значимые UI-элементы имеют help-сноски со ссылками на ТЗ и бизнес-процессы |
| Evidence | Каждый UI/process sprint дает HTML report со скриншотами и шагами тестирования |

## 3. Обновленная Линейка Спринтов

| Sprint | Name | Scope | Status |
| --- | --- | --- | --- |
| PN-1 | Backend Map Contract | `/map`, `/alerts`, `/drilldown` | Completed |
| PN-2 | UI Process Navigator Shell | route, ECharts map, alert panel, screenshot report | Completed |
| PN-3 | Navigator Contract Hardening | env selector backend, snapshot mode, pagination, generated_at, config manifest | Completed |
| PN-4 | Conformance And Versions | async conformance jobs, cached summary, process version breakdown | Completed |
| PN-5 | Performance And SLA | cycle time, waiting time, throughput, endpoint SLA tests | Completed |
| PN-6 | Infrastructure And Alert Correlation | infrastructure health, causal chains, deduplication | Completed |
| PN-7 | Business Key Tracking | SKU/store process trail, search integration, masked instance IDs | Completed |
| PN-8 | RBAC And Supplier Block | role matrix, supplier deny, scope filtering, audit access | Completed |
| PN-9 | UI Detail Panels And Help | conformance/performance/version/detail panels with help-сноски | Completed |
| PN-10 | Accessibility And Refresh | WCAG 2.1 AA, keyboard map, polling/staleness, axe-core | Completed |
| PN-11 | Reporting And Superset Payload | weekly report endpoint, Airflow digest, BI dataset contract | Completed |
| PN-12 | Load, Regression And Presentation | performance gate, HTML reports, stakeholder/developer presentation | Planned |

## 4. Спринты

### PN-3. Navigator Contract Hardening

Цель: подготовить backend foundation для расширенного navigator.

Функциональность:

- `env` parameter для `/process-navigator/*`;
- validation через `OPEN_FNR_ALLOWED_ENVIRONMENTS`;
- snapshot mode через `business_date`;
- alert pagination;
- `generated_at` и `data_freshness_seconds`;
- config values для refresh, TTL, dedup и pagination;
- обновление `CONFIGURATION_MANIFEST.md`.

Process Engine artifacts:

| Тип | Решение |
| --- | --- |
| BPMN | новые runtime artifacts не требуются |
| DMN | новые decision artifacts не требуются |
| CMMN | новые case artifacts не требуются |

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | env validation, snapshot mode, pagination, generated_at |
| Config | все параметры читаются из Settings |
| Quality | no hardcoded network config, text encoding |

Acceptance criteria:

- неизвестное окружение отклоняется;
- `business_date` включает snapshot mode;
- alerts ограничиваются page size;
- все новые параметры описаны в `.env.example` и `CONFIGURATION_MANIFEST.md`.

### PN-4. Conformance And Versions

Цель: показать соответствие фактического исполнения BPMN модели и разбор версий.

Функциональность:

- `POST /process-navigator/processes/{key}/conformance/check`;
- `GET /process-navigator/processes/{key}/conformance/status/{job_id}`;
- `GET /process-navigator/processes/{key}/conformance`;
- `summary_only=true` для badge;
- `GET /process-navigator/processes/{key}/versions`;
- cache TTL из config.

Process Engine artifacts:

| Тип | Решение |
| --- | --- |
| BPMN | используются существующие executable BPMN и Flowable History |
| DMN | governed API artifact для severity interpretation в будущем, без runtime adapter |
| CMMN | governed case для conformance incident в будущем, без runtime adapter |

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | async job lifecycle, cached summary, non-BPMN rejection |
| BPMN cognitive | skipped mandatory step, unexpected sequence |
| Performance | conformance request не блокирует `/map` |
| UI later | badge и deviation list |

Acceptance criteria:

- conformance расчет асинхронен;
- summary badge не запускает тяжелый расчет;
- version breakdown доступен и не схлопывается.

### PN-5. Performance And SLA

Цель: добавить процессные метрики производительности и SLA pass/fail targets.

Функциональность:

- `GET /process-navigator/processes/{key}/performance`;
- cycle time median/P95/max;
- waiting time vs processing time;
- throughput by business day;
- rework rate;
- P95 alert `cycle time P95 exceeds SLA`.

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | корректные поля performance response |
| SLA | threshold bands из config/governance |
| Load | P95 endpoint SLA |
| UI later | mini-chart и red/amber/green bands |

Acceptance criteria:

- performance metrics доступны по BPMN process key;
- SLA thresholds не хардкодятся в UI;
- P95 breach превращается в alert.

### PN-6. Infrastructure And Alert Correlation

Цель: связать бизнес-алерты с инфраструктурой и root cause chain.

Функциональность:

- `GET /process-navigator/infrastructure/health`;
- `infrastructure_dependencies`;
- alert `cause_chain`;
- directed causal edges;
- alert deduplication group with `occurrence_count`.

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | health response, dependent processes |
| Algorithm | BFS cause chain, cycle-safe traversal |
| Dedup | grouping by type/process/source/window |
| UI later | root cause badge и causal edge tooltip |

Acceptance criteria:

- root cause отличается от cascaded effect;
- high-frequency alerts сгруппированы;
- infrastructure risk виден в process context.

### PN-7. Business Key Tracking

Цель: дать оператору путь SKU/store или order proposal через все процессы.

Функциональность:

- `GET /process-navigator/tracking`;
- business key types: `sku-store`, `forecast-run`, `order-proposal`, `replenishment-cycle`, `promo`;
- masked instance IDs;
- timeline process trail.

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | required params, empty trail, masked instance IDs |
| Config | business key formats config-driven |
| Integration | trail covers pilot domains |
| UI later | search opens trail view |

Acceptance criteria:

- пользователь вводит SKU/store и видит process journey;
- instance IDs маскируются по RBAC policy;
- business key formats не хардкодятся.

### PN-8. RBAC And Supplier Block

Цель: реализовать role matrix для Process Navigator.

Функциональность:

- backend role enforcement через `policy.py`;
- supplier denied for all navigator endpoints;
- domain scope filtering;
- audit trail access by role;
- masked/unmasked instance IDs.

Тесты:

| Класс | Проверки |
| --- | --- |
| Security | admin, planner, store_manager, supplier, auditor, service_account |
| RBAC negative | forbidden endpoints return access denied |
| UI later | route hidden for supplier |

Acceptance criteria:

- role matrix покрыта positive/negative tests;
- supplier blocked на backend;
- UI не раскрывает недоступные действия.

### PN-9. UI Detail Panels And Help

Цель: вывести расширенные данные в UI с help-сносками.

Функциональность:

- conformance panel;
- performance panel;
- version panel;
- infrastructure risk tooltip;
- business key trail;
- help footnotes with spec/process refs.

Тесты:

| Класс | Проверки |
| --- | --- |
| UI E2E | panels open, data loads, errors shown |
| Help | every significant element has help-сноска |
| Visual | screenshots for panels and tooltips |
| Process | help links point to BPMN/DMN/CMMN or spec |

Acceptance criteria:

- все новые UI controls имеют help-сноски;
- пользователь видит связанный бизнес-процесс и постановку задачи;
- HTML UI/process report содержит screenshots.

### PN-10. Accessibility And Refresh

Цель: обеспечить WCAG 2.1 AA и live refresh без hardcoded intervals.

Функциональность:

- keyboard navigation;
- ECharts aria labels;
- reduced motion;
- contrast checks;
- polling via config;
- staleness warning.

Тесты:

| Класс | Проверки |
| --- | --- |
| Accessibility | axe-core route check |
| Keyboard | Tab, Enter, Escape |
| Refresh | generated_at, manual refresh, stale state |
| Config | intervals from config |

Acceptance criteria:

- route `#/process-navigator` проходит accessibility gate;
- refresh не хардкодится;
- stale data явно видна пользователю.

### PN-11. Reporting And Superset Payload

Цель: дать weekly digest и BI payload для stakeholders.

Функциональность:

- `GET /process-navigator/reports/weekly`;
- Airflow DAG `process_health_digest.py`;
- ClickHouse/Superset dataset contract;
- notification routing через Supplement 1 section K.

Тесты:

| Класс | Проверки |
| --- | --- |
| Backend | weekly report payload |
| Airflow | DAG import and payload build |
| Config | Superset host/port from env |
| Report | HTML/PDF-ready JSON |

Acceptance criteria:

- weekly report payload стабилен;
- digest не зависит от ручного UI входа;
- BI dataset documented.

### PN-12. Load, Regression And Presentation

Цель: закрыть большой блок Process Navigator промышленной проверкой и презентацией.

Функциональность:

- performance tests for 100 concurrent users;
- full PN regression;
- HTML test report;
- developer/user presentation with screenshots.

Тесты:

| Класс | Проверки |
| --- | --- |
| Load | endpoint P95 targets |
| Regression | PN-1..PN-11 pass |
| UI | screenshots and visual regression |
| Process | BPMN/DMN/CMMN references are complete |

Acceptance criteria:

- все PN tests зеленые;
- создан отчет `docs/test-reports/sprint-pn-final/index.html`;
- создана презентация для разработчиков и пользователей.

## 5. Текущий Статус

Статус после завершения `PN-9`:

- `PN-1` завершен: backend map contract.
- `PN-2` завершен: routed Process Navigator shell.
- `PN-3` завершен: env, snapshot, pagination и generated metadata.
- `PN-4` завершен: conformance evaluator и version contracts.
- `PN-5` завершен: process performance metrics.
- `PN-6` завершен: infrastructure health, causal alert chains и deduplication.
- `PN-7` завершен: business key tracking.
- `PN-8` завершен: backend RBAC boundary и supplier block.
- `PN-9` завершен: UI detail panels, contextual help footnotes и HTML evidence report.

Осталось `1` PN-спринт: `PN-12` load/regression/presentation.
