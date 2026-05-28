# Data Governance OPEN FNR

## 1. Назначение

Документ фиксирует владение данными, требования к качеству, SLA, MDM, правила исправлений и ответственность за данные.

## 2. Ключевые Домены Данных

| Домен | Источник | Владелец |
| --- | --- | --- |
| Продажи | POS/DWH | Sales Data Owner |
| Остатки | ERP/WMS | Inventory Data Owner |
| Цены | ERP/Pricing | Pricing Data Owner |
| Промо | Promo System | Promo Data Owner |
| Товары | MDM/PIM | Product Data Steward |
| Магазины | MDM | Store Data Steward |
| Поставщики | ERP/MDM | Supplier Data Owner |
| РЦ | WMS/MDM | DC Data Owner |
| Заказы | ERP/WMS | Order Data Owner |
| Календарь | Internal/External | Calendar Data Owner |
| Полка и выкладка | Planogram/Store Ops/Promo | Shelf Space Data Owner |
| Capacity | WMS/TMS/Store Ops | Capacity Data Owner |
| Supplier Performance | ERP/WMS | Supplier Performance Owner |
| Store Tasks | Store App/Operations | Store Operations Data Owner |
| True Inventory | POS/WMS/ERP derived | Inventory Data Owner |

## 3. Data Ownership

Каждый домен данных должен иметь:

- бизнес-владельца;
- технического владельца;
- data steward;
- SLA загрузки;
- правила качества;
- канал исправления ошибок;
- справочник бизнес-терминов.

## 4. Data Quality Dimensions

| Измерение | Проверка |
| --- | --- |
| Completeness | все обязательные поля заполнены |
| Validity | значения соответствуют типам и диапазонам |
| Uniqueness | нет дублей по бизнес-ключам |
| Consistency | данные согласованы между системами |
| Timeliness | данные пришли вовремя |
| Accuracy | данные соответствуют факту |
| Referential Integrity | все ключи маппятся на MDM |

## 5. SLA Данных

| Домен | SLA |
| --- | --- |
| Продажи | до начала ежедневного расчета |
| Остатки | до начала replenishment |
| Цены | до построения future features |
| Промо | до расчета promo uplift |
| MDM | актуальность на дату расчета |
| Открытые заказы | до расчета projected stock |
| Поставщики/РЦ | до расчета order proposals |

## 6. Критичность Ошибок

| Уровень | Описание | Действие |
| --- | --- | --- |
| Critical | расчет или публикация невозможны | блокировка |
| High | результат может быть существенно искажен | degraded mode или review |
| Medium | локальный эффект | warning |
| Low | не влияет на расчет | log only |

## 7. MDM-Требования

Обязательные master data:

- `sku_id`;
- `store_id`;
- `supplier_id`;
- `dc_id`;
- category hierarchy;
- store hierarchy;
- product lifecycle status;
- assortment status;
- replacement links;
- pack hierarchy.
- shelf hierarchy;
- store zone hierarchy;
- supplier hierarchy;
- capacity calendars.

## 8. Правила Исправлений

1. Ошибка регистрируется как Data Quality Incident.
2. Назначается data owner.
3. Указывается affected scope.
4. Определяется критичность.
5. Исправление выполняется в source system, если возможно.
6. Если source correction невозможна до расчета, используется approved override.
7. Override имеет срок действия.
8. Все исправления логируются.

## 9. Data Lineage

Для каждого прогноза и заказа должна быть возможность восстановить:

- исходные продажи;
- остатки;
- цены;
- промо;
- справочники;
- версии признаков;
- версию модели;
- версию бизнес-правил;
- ручные корректировки.

## 10. Data Governance Board

Состав:

- Data Owner по доменам;
- Product Owner;
- Data Platform Owner;
- ML Owner;
- Process Owner;
- Security Owner.

Рассматривает:

- критичные DQ incidents;
- изменения справочников;
- изменения бизнес-терминов;
- SLA источников;
- качество MDM;
- правила overrides.

## 11. Критерии Приемки

- у каждого домена есть владелец;
- DQ checks реализованы;
- критичные ошибки блокируют публикацию;
- MDM покрывает ключевые сущности;
- data lineage доступен;
- overrides версионируются;
- SLA данных мониторится.
