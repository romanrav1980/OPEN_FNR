# Security Strategy OPEN FNR

## 1. Назначение

Документ описывает стратегию безопасности OPEN FNR: RBAC, аудит, секреты, доступы, сервисные аккаунты, сегментацию данных и требования к production-контру.

## 2. Принципы

- least privilege;
- separation of duties;
- all changes audited;
- no shared admin accounts;
- secrets outside source code;
- service-to-service authentication;
- data access by role and scope;
- production access controlled;
- security by default.

## 3. Identity And Access

Рекомендуемый подход:

- интеграция с корпоративным IdP через OpenID Connect;
- RBAC на уровне приложения;
- optional ABAC по региону, категории, роли;
- service accounts для интеграций;
- регулярный access review.

## 4. Роли

| Роль | Доступ |
| --- | --- |
| Viewer | только просмотр |
| Forecast Planner | прогнозы и корректировки прогноза |
| Replenishment Planner | заказы и исключения пополнения |
| Promo Planner | промо-процессы |
| Fresh Manager | fresh-процессы |
| Category Manager | категория, промо, lifecycle |
| Data Engineer | DQ, ingestion, technical logs |
| Data Scientist | модели, метрики, backtesting |
| Admin | пользователи, роли, настройки |
| Auditor | audit trail, read-only |

## 5. Scope-Based Access

Доступ должен ограничиваться:

- регионом;
- форматом магазина;
- категорией;
- поставщиком;
- локацией;
- ролью процесса.

## 6. Audit

Аудируются:

- login/logout;
- просмотр критичных данных;
- изменения прогноза;
- изменения заказа;
- изменения правил;
- изменения BPMN/DMN/CMMN;
- publication/export;
- access changes;
- admin actions.

## 7. Secrets Management

Секреты:

- не хранятся в git;
- не передаются в логах;
- ротируются;
- выдаются через runtime secret storage;
- имеют владельца.

## 8. Data Protection

Требования:

- TLS для сетевого обмена;
- шифрование backup;
- контроль доступа к ClickHouse/PostgreSQL;
- маскирование чувствительных данных, если есть;
- ограничение выгрузок;
- audit exports.

## 9. Service Security

Для сервисов:

- service accounts;
- mTLS или token-based auth;
- network policies;
- rate limits;
- input validation;
- dependency scanning;
- container image scanning.

## 10. Process Engine Security

Flowable должен учитывать:

- task assignment by role;
- process admin rights;
- model deployment rights;
- DMN edit rights;
- CMMN case access;
- audit of process actions.

## 11. Security Testing

Проверяются:

- RBAC;
- privilege escalation;
- unauthorized API access;
- broken object level authorization;
- secrets leakage;
- audit completeness;
- export permissions;
- admin actions.

## 12. Incident Response

Security incident должен иметь:

- severity;
- owner;
- timeline;
- containment plan;
- remediation plan;
- postmortem;
- access review.

## 13. Критерии Приемки

- RBAC реализован;
- scope-based access работает;
- audit trail доступен;
- секреты не в коде;
- service accounts разделены;
- admin actions audited;
- security regression tests есть;
- production access controlled.

