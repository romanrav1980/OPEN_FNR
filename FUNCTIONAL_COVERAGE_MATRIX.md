# Functional Coverage Matrix

## 1. Назначение

Документ фиксирует сверку функциональности из `raw/RELEX Modules and functionality RU.csv` с целевой функциональностью OPEN FNR.

Статусы:

| Статус | Значение |
| --- | --- |
| `BASE` | входит в базовый scope OPEN FNR |
| `MVP/PILOT` | входит в ранний контур MVP или пилота |
| `INDUSTRIAL` | входит в промышленную версию |
| `ADD-ON` | отдельный расширяемый модуль, не обязателен для базового расчета |
| `COVERED` | уже покрыто в документах |
| `ADDED` | добавлено по результатам сверки |

## 2. Сводная Матрица

| RELEX-модуль из raw | OPEN FNR coverage | Scope |
| --- | --- | --- |
| Базовое прогнозирование | regular forecast, ML forecast, DQ, anomalies, reference products, manual adjustments, dashboards | `BASE / COVERED` |
| Интегрированные цепочки поставок | DC forecast from store order forecasts, cross-docking, upstream visibility, chain inventory projection | `INDUSTRIAL / ADDED` |
| Пополнение запасов | projected stock, demand projection, order proposals, safety/presentation stock, constraints | `BASE / COVERED` |
| Оптимизация свежих товаров | shelf-life, spoilage, FEFO, fresh order optimization | `INDUSTRIAL / COVERED` |
| Сезонное планирование | seasonal allocation, seasonal purchasing sync, end-of-season clearance | `INDUSTRIAL / ADDED` |
| Многоканальный спрос ритейлера | store, DC, e-commerce, dark store demand planning | `INDUSTRIAL / PARTIAL` |
| Промоакции и события | promo uplift, events, promo supply, post-promo review | `BASE / COVERED` |
| Оптимизация закупок | multi-supplier selection, target shares, purchasing constraints, supplier calendars | `INDUSTRIAL / ADDED` |
| Оптимизация полочного пространства | shelf capacity, delivery consolidation by store zone, direct-to-shelf | `INDUSTRIAL / ADDED` |
| Оптимизация мощностей | delivery smoothing, capacity limits, DC/store workload constraints | `INDUSTRIAL / ADDED` |
| Диагностика цепочек поставок | root-cause analysis for shortage, spoilage, overstock, DC issues | `INDUSTRIAL / ADDED` |
| Планирование, оптимизация и оценка промо | promo evaluation, cannibalization, stockpiling, halo, best/worst promo analysis | `INDUSTRIAL / ADDED` |
| Планирование каналов оптовой торговли | wholesale/B2B channel planning | `ADD-ON / ADDED` |
| True Inventory | virtual inventory from POS transactions, stock correction when inventory data is missing | `ADD-ON / ADDED` |
| Управление магазином | mobile replenishment, store tasks, store execution feedback | `ADD-ON / ADDED` |
| Сотрудничество с поставщиками | supplier collaboration, shared forecasts, supplier performance, supply exceptions | `INDUSTRIAL / ADDED` |
| Прогнозирование рабочей нагрузки | store/DC workload forecasting from sales, deliveries and replenishment | `ADD-ON / ADDED` |
| Комплект конфигурации | configurable business rules, dashboards, workflows | `BASE / COVERED via Flowable + configurable UI` |

## 3. Функции, Добавленные В Scope После Сверки

### 3.1. Integrated Supply Chain

- прогноз РЦ на основе forecast/order forecast магазинов;
- cross-docking flow planning;
- видимость потребности вверх по цепочке;
- согласование заказов магазин -> РЦ -> поставщик;
- upstream forecast sharing.

### 3.2. Procurement Optimization

- выбор поставщика при нескольких поставщиках;
- целевые доли поставщиков;
- графики поставщиков;
- lead time;
- MOQ/MOV;
- ограничения закупки;
- закупочные предложения для РЦ.

### 3.3. Shelf Space Optimization

- учет места выкладки;
- мощность выкладки;
- shelf capacity;
- consolidation of deliveries by store area;
- direct-to-shelf replenishment.

### 3.4. Capacity Optimization

- сглаживание поставок внутри недели;
- ограничения РЦ;
- ограничения транспорта;
- ограничения приемки магазина;
- workload-aware order shaping.

### 3.5. Supply Chain Diagnostics

- root cause дефицита;
- root cause порчи;
- root cause overstock;
- root cause DC shortage;
- root cause supplier failures.

### 3.6. Promo Evaluation

- анализ promo uplift;
- cannibalization;
- stockpiling;
- halo effect;
- post-promo dip;
- best/worst promo ranking.

### 3.7. True Inventory

- расчет виртуального остатка из POS-транзакций;
- поддержка категорий без надежных stock balances;
- рекомендации по корректировке остатка;
- confidence score виртуального остатка.

### 3.8. Store Management

- mobile-friendly store replenishment view;
- store task list;
- подтверждение выкладки;
- feedback по stock-out, shelf availability, display execution.

### 3.9. Supplier Collaboration

- передача forecast/order forecast поставщикам;
- мониторинг fill rate;
- supply risk alerts;
- supplier exception workflow.

### 3.10. Workload Forecasting

- прогноз рабочей нагрузки магазина и РЦ;
- workload from deliveries;
- workload from shelf replenishment;
- workload from promo execution;
- интеграция с capacity smoothing.

## 4. Принцип Scope

Не все функции входят в первый MVP. Для управления scope функции разделены:

- `BASE`: критично для ядра forecast/replenishment;
- `INDUSTRIAL`: нужно для промышленного масштаба;
- `ADD-ON`: отдельный расширяемый модуль после стабилизации ядра.

