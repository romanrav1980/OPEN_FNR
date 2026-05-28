# План Разработки По Спринтам OPEN FNR

## 1. Назначение

Документ описывает план разработки OPEN FNR в разрезе спринтов. Каждый спринт должен давать законченную мини-функциональность, которую можно показать, протестировать и использовать как основу для следующего слоя.

План учитывает:

- прогнозирование регулярного спроса;
- промо-прогноз;
- пополнение запасов;
- Process Engine;
- UI;
- интеграции;
- data governance;
- ML governance;
- тестирование;
- нагрузку и SLA;
- Apache-2.0 compatible стек;
- целевой production-контур на AMD EPYC.

## 2. Результат Проверки Документов

Перед планированием были сверены текущие документы:

- [PROJECT_CHARTER.md](PROJECT_CHARTER.md)
- [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)
- [TECHNOLOGY_ARCHITECTURE.md](TECHNOLOGY_ARCHITECTURE.md)
- [PRODUCT_VISION.md](PRODUCT_VISION.md)
- [ROADMAP.md](ROADMAP.md)
- [TARGET_OPERATING_MODEL.md](TARGET_OPERATING_MODEL.md)
- [KPI_BUSINESS_VALUE_FRAMEWORK.md](KPI_BUSINESS_VALUE_FRAMEWORK.md)
- [DATA_GOVERNANCE.md](DATA_GOVERNANCE.md)
- [PROCESS_ENGINE_GOVERNANCE.md](PROCESS_ENGINE_GOVERNANCE.md)
- [INTEGRATION_STRATEGY.md](INTEGRATION_STRATEGY.md)
- [ML_GOVERNANCE.md](ML_GOVERNANCE.md)
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- [SECURITY_STRATEGY.md](SECURITY_STRATEGY.md)
- [BUSINESS_PROCESS_DETAILED_SPEC.md](BUSINESS_PROCESS_DETAILED_SPEC.md)
- [BUSINESS_PROCESSES_UI_SPEC.md](BUSINESS_PROCESSES_UI_SPEC.md)
- [UI_TESTING_SPEC.md](UI_TESTING_SPEC.md)

Найденное противоречие:

| Область | Было | Исправлено |
| --- | --- | --- |
| Инфраструктура | в старом разделе ТЗ допускался `Intel Xeon` как production-ориентир | целевой production-контур зафиксирован на `AMD EPYC 9004/9005` |

Зафиксированные единые решения:

- стек только free self-hosted open-source с permissive-лицензиями;
- `Flowable OSS` как `OPEN FNR Process Engine`;
- `BPMN/DMN/CMMN` для процессов, правил и исключений;
- `Spark + Polars + ClickHouse + PostgreSQL`;
- `Apache Airflow` для batch orchestration;
- `Kubernetes + containerd/nerdctl`;
- `React + Apache ECharts + Apache Superset`;
- production sizing на EPYC-кластере;
- GPU не обязателен для первой промышленной версии.

## 3. Общая Модель Спринта

Рекомендуемая длительность спринта: `2 недели`.

Каждый спринт должен иметь:

- бизнес-цель;
- ограниченный функциональный scope;
- работающий вертикальный результат;
- тесты данных;
- backend/API тесты;
- Process Engine тесты, если затронут процесс;
- UI тесты, если есть интерфейс;
- нагрузочные или performance smoke tests;
- security/RBAC проверки, если есть доступы;
- демонстрацию результата;
- обновление документации.

## 4. Definition Of Done Для Любого Спринта

Спринт считается завершенным, если:

- функциональность работает в `DEV` или `TEST`;
- есть automated tests для измененного слоя;
- API имеет OpenAPI-контракт;
- миграции БД применяются автоматически;
- ошибки логируются;
- audit trail реализован там, где есть бизнес-действия;
- UI не содержит hardcoded process transitions, если процесс управляется Flowable;
- документация обновлена;
- known limitations записаны;
- demo проведено.

## 5. Фазы Разработки

```mermaid
flowchart LR
    A[Foundation] --> B[Data]
    B --> C[Forecast]
    C --> D[Promo]
    D --> E[Replenishment]
    E --> F[Process Engine]
    F --> G[UI Workbenches]
    G --> H[Integrations]
    H --> I[Scale & Production]
```

## 6. Спринт 0. Project Bootstrap

### Цель

Подготовить инженерную основу проекта.

### Функциональность

- структура репозиториев;
- базовый monorepo или multi-repo layout;
- coding standards;
- CI skeleton;
- container runtime без Docker Desktop;
- базовые окружения `DEV/TEST`;
- шаблоны ADR, API contract, migrations, test reports.

### Технический Scope

- Kubernetes local/dev profile или Linux services profile;
- PostgreSQL dev;
- ClickHouse dev;
- Airflow dev;
- Flowable dev;
- FastAPI skeleton;
- React skeleton;
- OpenAPI generation skeleton.

### Тесты

| Тип | Проверка |
| --- | --- |
| Smoke | все сервисы стартуют |
| API | `/health` отвечает |
| UI | стартовая страница открывается |
| CI | pipeline выполняется |
| Security | секреты не лежат в репозитории |

### Выход

Рабочий технический каркас.

## 7. Спринт 1. Data Ingestion Foundation

### Цель

Заложить базовый слой загрузки данных.

### Функциональность

- загрузка продаж;
- загрузка остатков;
- загрузка цен;
- загрузка MDM товаров и магазинов;
- raw/clean layout;
- batch metadata.

### Тесты

| Тип | Проверка |
| --- | --- |
| Data | schema validation, row count, null checks |
| API | статус загрузки |
| UI | Data Quality Console: список загрузок |
| Performance | загрузка тестового объема за лимит |
| Business Process | Data Load status lifecycle |

### Выход

Данные базовых доменов доступны в clean layer.

## 8. Спринт 2. Data Quality Console

### Цель

Сделать DQ видимым и управляемым.

### Функциональность

- DQ checks;
- severity;
- blocking/non-blocking errors;
- DQ incidents;
- Data Quality Console;
- audit загрузок.

### Тесты

| Тип | Проверка |
| --- | --- |
| Data | дубли, nulls, referential integrity |
| UI | ошибки видны, фильтруются, открываются |
| Process | DQ incident case создается |
| API | DQ endpoints |
| Security | доступ только Data Engineer/Admin |

### Выход

Пользователь видит качество данных и блокирующие ошибки.

## 9. Спринт 3. Active Matrix And Feature Mart

### Цель

Построить активную матрицу и первые признаки.

### Функциональность

- active `store x SKU` matrix;
- calendar features;
- lag features;
- rolling features;
- price features;
- stock availability flags;
- feature mart versioning.

### Тесты

| Тип | Проверка |
| --- | --- |
| Data | active matrix не содержит закрытые магазины/SKU |
| ML/Data | признаки point-in-time корректны |
| Performance | feature build на тестовом shard |
| API | feature mart metadata |
| Regression | golden dataset comparison |

### Выход

Готова основа для baseline forecast.

## 10. Спринт 4. Regular Forecast Baseline

### Цель

Получить первый регулярный прогноз.

### Функциональность

- seasonal naive / rolling median baseline;
- forecast output schema;
- forecast versioning;
- WAPE/Bias calculation;
- запись в ClickHouse.

### Тесты

| Тип | Проверка |
| --- | --- |
| ML | WAPE/Bias считаются корректно |
| Data | forecast rows match active matrix x horizon |
| API | получить forecast latest |
| UI | Forecast Workbench read-only |
| Performance | scoring baseline на shard |

### Выход

Первый ежедневный прогноз regular спроса.

## 11. Спринт 5. Forecast Workbench V1

### Цель

Дать пользователю рабочий просмотр прогноза.

### Функциональность

- фильтры по дате, магазину, SKU, категории;
- таблица прогноза;
- график факт vs прогноз;
- WAPE/Bias view;
- drill-down.

### Тесты

| Тип | Проверка |
| --- | --- |
| UI E2E | открыть forecast, отфильтровать, drill-down |
| API | pagination/filtering |
| Performance UI | фильтр до 5 секунд |
| RBAC | Viewer read-only |
| Visual | таблица и график не ломаются |

### Выход

Forecast Planner может просматривать регулярный прогноз.

## 12. Спринт 6. ML Regular Model V1

### Цель

Заменить baseline первой ML-моделью.

### Функциональность

- LightGBM/CatBoost training;
- MLflow registry;
- backtesting;
- model approval draft;
- inference job;
- fallback на baseline.

### Тесты

| Тип | Проверка |
| --- | --- |
| ML | ML лучше baseline на пилотном срезе |
| ML Governance | модель имеет версию и approval status |
| Performance | inference runtime на shard |
| Regression | fallback работает |
| API | model metadata |

### Выход

Production-candidate модель регулярного спроса.

## 13. Спринт 7. Promo Data Model And Validation

### Цель

Завести промо как управляемый объект.

### Функциональность

- promo entity;
- обязательные поля: SKU, магазины, даты, цена, скидка, механика, место выкладки, мощность выкладки;
- validation rules;
- promo statuses;
- Promo Workbench draft UI.

### Тесты

| Тип | Проверка |
| --- | --- |
| UI Validation | промо без SKU/цены/выкладки не проходит |
| DMN | Promo Completeness decision |
| API | create/update promo |
| Data | promo overlaps detection |
| RBAC | Promo Planner может редактировать |

### Выход

Промо-план можно завести и проверить на полноту.

## 14. Спринт 8. Promo Uplift Forecast V1

### Цель

Рассчитать первый промо-uplift.

### Функциональность

- regular baseline на период промо;
- uplift model/baseline;
- total forecast = regular + uplift;
- reference promo comparison;
- promo forecast view.

### Тесты

| Тип | Проверка |
| --- | --- |
| ML | uplift считается отдельно |
| UI | regular/uplift/total отображаются |
| Business Process | promo status `forecasted` |
| Performance | promo scoring на тестовом объеме |
| Regression | промо не загрязняет regular forecast |

### Выход

Пользователь видит прогноз промо и uplift.

## 15. Спринт 9. Process Engine Foundation

### Цель

Подключить Flowable как процессный слой.

### Функциональность

- Flowable deployment;
- Process API adapter;
- user tasks;
- task list UI;
- BPMN skeleton for Promo Planning;
- DMN integration.

### Тесты

| Тип | Проверка |
| --- | --- |
| Process | BPMN happy path запускается |
| DMN | decision table возвращает результат |
| API | task list, complete task |
| UI | пользователь видит задачи |
| Audit | процессные действия пишутся |

### Выход

Первый процесс исполняется не через hardcode, а через Process Engine.

## 16. Спринт 10. Promo Approval Process

### Цель

Сделать end-to-end процесс согласования промо.

### Функциональность

- BPMN Promo Planning;
- роли Promo Planner, Category Manager, Supply Chain;
- DMN risk classification;
- approval/reject/rework;
- process history in UI.

### Тесты

| Тип | Проверка |
| --- | --- |
| Process | happy path и reject path |
| UI E2E | создать промо -> forecast -> approve |
| RBAC | только нужная роль согласует |
| Audit | все решения видны |
| Regression | статусы приходят из Flowable |

### Выход

Промо можно согласовать управляемым процессом.

## 17. Спринт 11. Replenishment Foundation

### Цель

Рассчитать первую потребность и projected stock.

### Функциональность

- current stock;
- open orders;
- in-transit;
- lead time;
- projected stock;
- demand projection;
- Replenishment Mart schema.

### Тесты

| Тип | Проверка |
| --- | --- |
| Data | stock/open orders join корректен |
| Business Logic | projected stock formula |
| API | inventory projection endpoint |
| UI | Inventory Projection view |
| Performance | расчет projected stock на shard |

### Выход

Система показывает будущие остатки.

## 18. Спринт 12. Order Proposal V1

### Цель

Сформировать первые предложения заказов.

### Функциональность

- gross requirement;
- net requirement;
- safety stock;
- presentation stock;
- MOQ/rounding;
- order proposal;
- explanation.

### Тесты

| Тип | Проверка |
| --- | --- |
| Business Logic | формула заказа |
| UI | order explanation видна |
| API | proposals endpoint |
| Regression | округление по коробу |
| Performance | расчет order proposals на shard |

### Выход

Планировщик видит объяснимое предложение заказа.

## 19. Спринт 13. Replenishment Workbench V1

### Цель

Дать планировщику рабочий интерфейс заказов.

### Функциональность

- список proposals;
- фильтры по поставщику, РЦ, магазину, категории;
- approve/reject/adjust;
- preview корректировки;
- audit trail.

### Тесты

| Тип | Проверка |
| --- | --- |
| UI E2E | открыть, изменить, подтвердить заказ |
| RBAC | Forecast Planner не меняет заказ |
| Audit | корректировка заказа записана |
| Performance UI | фильтр до 5 секунд |
| Process | Replenishment Approval process basic |

### Выход

Пользователь может принять или изменить заказ.

## 20. Спринт 14. Exception Center V1

### Цель

Собрать исключения в единый рабочий центр.

### Функциональность

- exception model;
- stock-out risk;
- overstock risk;
- promo shortage risk;
- supplier constraint;
- exception statuses;
- Exception Center UI;
- CMMN skeleton.

### Тесты

| Тип | Проверка |
| --- | --- |
| CMMN | case lifecycle |
| UI E2E | взять в работу, закрыть, эскалировать |
| API | exception filtering |
| RBAC | владелец видит свои исключения |
| Performance | список исключений до 3 секунд |

### Выход

Пользователь работает с исключениями, а не со всем объемом заказов.

## 21. Спринт 15. Manual Adjustments Framework

### Цель

Сделать безопасный слой ручных корректировок.

### Функциональность

- adjustment entity;
- reason codes;
- validity period;
- preview impact;
- apply/cancel;
- audit trail;
- effect reporting.

### Тесты

| Тип | Проверка |
| --- | --- |
| UI | корректировка требует причину |
| Business Logic | final forecast/order учитывает adjustment |
| Audit | старое/новое значение сохранено |
| RBAC | права по ролям |
| Regression | ML forecast не затирается |

### Выход

Ручные изменения управляемы и проверяемы.

## 22. Спринт 16. Publication And Export V1

### Цель

Подготовить controlled export в DWH/ERP/WMS.

### Функциональность

- publication status;
- export package;
- idempotency key;
- ERP/WMS mock;
- retry;
- export failure exception;
- export audit.

### Тесты

| Тип | Проверка |
| --- | --- |
| Integration | mock принимает forecast/order |
| API | idempotent export |
| Process | Publication Process |
| UI | export status виден |
| Failure | ошибка создает exception |

### Выход

Заказы и прогнозы можно публиковать в тестовый внешний контур.

## 23. Спринт 17. Accuracy And KPI Dashboards

### Цель

Сделать бизнес-метрики видимыми.

### Функциональность

- WAPE/Bias dashboard;
- service level;
- stock-out rate;
- overstock;
- manual adjustment effect;
- proposal acceptance rate;
- business value draft.

### Тесты

| Тип | Проверка |
| --- | --- |
| Data | метрики совпадают с контрольным расчетом |
| UI | drill-down сеть -> категория -> SKU |
| Performance | dashboard до 5 секунд |
| Regression | фильтры не искажают KPI |
| UAT | бизнес подтверждает понятность |

### Выход

Руководство и владельцы процессов видят эффект.

## 24. Спринт 18. Fresh V1

### Цель

Добавить базовую поддержку fresh.

### Функциональность

- shelf-life fields;
- batches;
- expected waste;
- fresh projected stock;
- fresh order warning;
- Fresh Workbench V1.

### Тесты

| Тип | Проверка |
| --- | --- |
| Business Logic | expected waste |
| UI | shelf-life и spoilage risk видны |
| Exception | high spoilage case |
| Performance | fresh calculation shard |
| Regression | FEFO ordering |

### Выход

Fresh Manager видит риск списаний и может влиять на заказ.

## 25. Спринт 19. Lifecycle SKU V1

### Цель

Поддержать ввод и вывод SKU.

### Функциональность

- phase-in;
- reference product;
- phase-out;
- termination date;
- replacement link;
- lifecycle warnings.

### Тесты

| Тип | Проверка |
| --- | --- |
| Business Process | phase-in/phase-out path |
| Forecast | new SKU fallback |
| Replenishment | заказ после termination date запрещен |
| UI | lifecycle status виден |
| Audit | изменения lifecycle сохраняются |

### Выход

Новые и выводимые товары корректно влияют на прогноз и заказ.

## 26. Спринт 20. Multi-Echelon V1

### Цель

Связать потребность магазинов и РЦ.

### Функциональность

- store demand aggregation to DC;
- DC stock;
- DC shortage;
- basic allocation;
- Supply Chain Dashboard.

### Тесты

| Тип | Проверка |
| --- | --- |
| Business Logic | потребность РЦ равна агрегату магазинов |
| UI | drill-down РЦ -> магазины |
| Exception | DC shortage |
| Performance | aggregation на тестовом объеме |
| Integration | WMS stock mock |

### Выход

Supply Chain видит потребность РЦ и дефицит.

## 27. Спринт 21. Performance Gate 1

### Цель

Проверить масштабируемость на pilot-scale.

### Функциональность

- synthetic load generator;
- shard runner;
- Spark/Polars profiling;
- ClickHouse write/read benchmarks;
- UI performance baseline;
- bottleneck report.

### Тесты

| Тип | Проверка |
| --- | --- |
| Load | active matrix pilot scale |
| Stress | peak partitions |
| DB | ClickHouse inserts and queries |
| API | forecast/proposals latency |
| UI | workbench filter latency |

### Выход

Понятен предел текущего контура и узкие места.

## 28. Спринт 22. Security And RBAC Hardening

### Цель

Довести безопасность до production-ready уровня.

### Функциональность

- RBAC;
- scope-based access;
- audit log;
- service accounts;
- secrets handling;
- admin console basics.

### Тесты

| Тип | Проверка |
| --- | --- |
| Security | unauthorized access denied |
| RBAC | роли не видят чужие действия |
| Audit | admin action logged |
| API | object-level authorization |
| Regression | existing flows still pass |

### Выход

Доступы и аудит готовы для пилота.

## 29. Спринт 23. Stage Rehearsal

### Цель

Провести end-to-end прогон в stage.

### Функциональность

- daily run rehearsal;
- DQ -> forecast -> promo -> replenishment -> exceptions -> publish;
- stage data snapshot;
- incident runbook draft;
- release checklist.

### Тесты

| Тип | Проверка |
| --- | --- |
| E2E | полный daily cycle |
| Process | все ключевые BPMN/CMMN paths |
| Integration | ERP/WMS/DWH mocks |
| Performance | cycle within target for stage |
| UAT | бизнес-пользователь проходит сценарий |

### Выход

Система готова к бизнес-пилоту.

## 30. Спринт 24. Business Pilot Release

### Цель

Выпустить пилот для ограниченной бизнес-зоны.

### Функциональность

- pilot categories;
- pilot users;
- daily operations;
- business KPI tracking;
- feedback collection;
- defect triage;
- adoption report.

### Тесты

| Тип | Проверка |
| --- | --- |
| UAT | пользователи работают по процессам |
| KPI | WAPE/Bias/service metrics считаются |
| Support | L1/L2 incidents handled |
| Regression | critical flows stable |
| Business | pilot acceptance |

### Выход

Бизнес-пилот запущен и измеряется.

## 31. Спринты 25-30. Industrialization

### Цель

Подготовить систему к industrial pilot и full production.

### Scope

- масштабирование категорий;
- расширение регионов;
- ClickHouse cluster tuning;
- Spark tuning;
- Airflow production hardening;
- Flowable process governance;
- ML retraining automation;
- DR procedures;
- production support;
- performance gate на full-scale projection.

### Тесты

| Тип | Проверка |
| --- | --- |
| Load | full-scale synthetic/projection |
| Resilience | отказ узла, retry, replay |
| DR | backup/restore rehearsal |
| Security | access review |
| Regression | full suite |
| Business | industrial acceptance |

### Выход

Система готова к промышленному масштабированию.

## 32. Спринты 31-36. Extended Functional Modules

### Цель

Закрыть расширенные функциональные модули, добавленные по результатам сверки с `raw/RELEX Modules and functionality RU.csv`.

### Sprint 31. Procurement Optimization

Функциональность:

- multi-supplier SKU;
- supplier selection;
- target supplier shares;
- purchase proposals;
- supplier constraints.

Тесты:

- supplier selection unit tests;
- purchase proposal API tests;
- supplier constraint UI tests;
- DMN rules for supplier choice;
- performance test на закупочном shard.

### Sprint 32. Shelf Space And Store Area Optimization

Функциональность:

- shelf capacity;
- direct-to-shelf;
- store zone consolidation;
- display stock validation;
- shelf capacity exceptions.

Тесты:

- UI validation места/мощности выкладки;
- order proposal recalculation tests;
- shelf capacity business rules;
- store zone filtering;
- visual regression для promo/shelf UI.

### Sprint 33. Capacity Optimization And Workload Forecasting

Функциональность:

- capacity workbench;
- delivery smoothing;
- workload forecast;
- overload risk;
- affected order preview.

Тесты:

- load smoothing unit tests;
- workload forecast golden dataset;
- capacity UI E2E;
- performance test на weekly delivery plan;
- audit test для переносов.

### Sprint 34. Supply Chain Diagnostics

Функциональность:

- root cause model;
- diagnostic insight cards;
- shortage/spoilage/overstock root causes;
- evidence view;
- create exception from diagnostic insight.

Тесты:

- root cause classification tests;
- diagnostics API tests;
- UI E2E root cause card;
- integration with Exception Center;
- regression test для linked evidence.

### Sprint 35. Supplier Collaboration

Функциональность:

- supplier dashboard;
- forecast sharing;
- order forecast export;
- supplier confirmation;
- supplier performance KPIs.

Тесты:

- supplier forecast export integration tests;
- fill rate metric tests;
- supplier exception CMMN tests;
- RBAC/scope tests для supplier view;
- UI E2E supplier confirmation.

### Sprint 36. True Inventory And Store Management

Функциональность:

- virtual stock calculation;
- confidence score;
- store task list;
- promo display confirmation;
- stock-out check task;
- store feedback loop.

Тесты:

- virtual stock calculation tests;
- confidence score tests;
- mobile/store UI tests;
- store task CMMN lifecycle;
- feedback integration tests.

## 33. Сквозная Матрица Тестов

| Слой | Минимальный тестовый набор |
| --- | --- |
| Data | schema, nulls, duplicates, freshness, MDM integrity |
| ML | backtesting, WAPE/Bias, fallback, drift smoke |
| Backend | unit, contract, integration, idempotency |
| Process | BPMN paths, DMN tables, CMMN lifecycle |
| UI | smoke, E2E, validation, visual, RBAC |
| Performance | batch runtime, DB read/write, API latency, UI latency |
| Security | RBAC, object-level auth, audit, secrets |
| Integration | mocks, retry, failure, export status |

## 34. Рекомендуемый Порядок Релизов

| Release | Спринты | Смысл |
| --- | --- | --- |
| R0 Foundation | 0-3 | данные и базовая платформа |
| R1 Forecast MVP | 4-6 | регулярный прогноз |
| R2 Promo MVP | 7-10 | промо и Process Engine |
| R3 Replenishment MVP | 11-16 | пополнение и публикация |
| R4 Business Analytics | 17-20 | KPI, fresh, lifecycle, multi-echelon |
| R5 Pilot Ready | 21-24 | performance, security, stage, pilot |
| R6 Industrial | 25-30 | масштабирование и production hardening |
| R7 Extended Modules | 31-36 | procurement, shelf, capacity, diagnostics, supplier, store |

## 35. Управленческие Контрольные Точки

| Gate | После | Решение |
| --- | --- | --- |
| G1 Data Ready | Sprint 3 | можно строить forecast |
| G2 Forecast Valuable | Sprint 6 | ML лучше baseline |
| G3 Promo Process Ready | Sprint 10 | промо управляется процессом |
| G4 Orders Explainable | Sprint 13 | replenishment понятен пользователю |
| G5 Pilot Ready | Sprint 23 | можно запускать бизнес-пилот |
| G6 Industrial Ready | Sprint 30 | можно масштабировать |
| G7 Extended Coverage Ready | Sprint 36 | закрыты функции raw-бенчмарка |
