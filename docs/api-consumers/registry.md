# OPEN FNR API Consumer Registry

Status: initial registry required by `TECHNICAL_SPEC_SUPPLEMENT_1.md`.

| Consumer | Team | API version | Endpoints | Contact | Status |
| --- | --- | --- | --- | --- | --- |
| Auto Order System | Supply Chain IT | `/api/v1/` | forecast export, order proposals | TBD | pending registration |
| ERP | ERP Team | `/api/v1/` | orders, prices, order statuses | TBD | pending registration |
| WMS | Logistics IT | `/api/v1/` | stock, open orders, in-transit | TBD | pending registration |
| DWH | Data Platform | `/api/v1/` | clean facts, marts, lineage | TBD | pending registration |
| BI | Analytics | `/api/v1/` | KPI, forecast accuracy, monitoring | TBD | pending registration |
| Supplier Collaboration | Procurement IT | `/supplier-api/v1/` | supplier forecast share, confirmations | TBD | pending registration |

Any public API deprecation must notify every registered consumer at least 90 days before sunset, except emergency security deprecation.
