# OPEN FNR Pilot Scope And Data Readiness Specification

Status: PILOT-1 foundation  
Date: 2026-05-29

## 1. Purpose

This document fixes the minimum pilot entry pack for OPEN FNR. The pilot may enter shadow mode only when business scope, source data coverage, history depth, active matrix, business calendar and acceptance thresholds are signed and visible through the backend.

## 2. Pilot Scope

| Dimension | Frozen Value |
| --- | --- |
| Scope id | `pilot-north-fresh-001` |
| Regions | north |
| Stores | 3 pilot stores |
| SKU count | 1200 pilot SKU |
| Categories | fresh, grocery |
| Suppliers | pilot fresh and grocery suppliers |
| Users | forecast planner, supply manager, business owner |

Scope sign-off endpoint:

```text
GET /pilot/scope-signoff
```

The sign-off must include Business Owner, Supply Chain Director, Data Platform Lead and IT Ops before shadow mode starts.

## 3. Data Readiness

Data readiness endpoint:

```text
GET /pilot/data-readiness
```

Required readiness areas:

| Area | Requirement |
| --- | --- |
| sales_history | 12-24 months of POS/DWH facts for pilot scope |
| stock_and_in_transit | WMS stock, in-transit and open-order contracts are ready |
| active_matrix | Pilot SKU/store active matrix is frozen |
| promo_history | Promo history is available for pilot categories |

Every item must be `ready`, have zero blockers and provide evidence.

## 4. Business Calendar

The pilot calendar must define:

- shadow mode start date;
- shadow evidence gate after the minimum shadow window;
- controlled export decision point.

The calendar is returned in `/pilot/readiness-pack`.

## 5. Acceptance Thresholds

| Metric | Direction |
| --- | --- |
| WAPE | less or equal than threshold |
| Service level | greater or equal than threshold |
| Lost sales reduction | greater or equal than threshold |
| Overstock reduction | greater or equal than threshold |
| Waste reduction | greater or equal than threshold |

Thresholds are business-owned and must be visible before shadow mode.

## 6. Acceptance Criteria

PILOT-1 is accepted when:

- `/pilot/readiness-pack`, `/pilot/data-readiness` and `/pilot/scope-signoff` are available;
- pilot scope includes stores, SKU count, categories and suppliers;
- all historical data areas with history requirements have at least 12 months of history;
- active matrix coverage is complete;
- acceptance thresholds include WAPE, service level, lost sales, overstock and waste;
- full regression remains green.
