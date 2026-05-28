# Open Questions

Open questions are tracked here until they become decisions, requirements or backlog items.

## Business

- What WAPE target is acceptable by category?
- What service level targets are required by category and ABC class?
- Which categories enter MVP?
- Which regions enter business pilot?
- What is the official definition of promo sales: full promo volume or uplift only?
- Which users can manually adjust forecast and orders?

## Data

- What is the true source of stock-on-hand?
- What is the SLA for D+1 sales data availability?
- Are open orders and in-transit reliable enough for projected stock?
- Is shelf-life data available at batch level?
- Are promo display location and display capacity stored today?

## Integration

- How does ERP accept order proposals?
- How does WMS provide delivery status?
- What idempotency keys can be used for exports?
- Is there an existing corporate MDM API?

## Process

- Which promo approval roles are mandatory for MVP?
- Which exceptions require CMMN case handling first?
- Who owns DMN rule changes?

## Infrastructure

- What EPYC node count is available for pilot?
- Is 100 GbE available in the target production environment?
- Which object storage option is preferred: Apache Ozone or SeaweedFS?

## Extended Functional Scope

- Which modules from the raw benchmark are mandatory for industrial pilot versus later add-on?
- Is supplier collaboration exposed to external supplier users or only internal supply chain users?
- Do stores need a mobile UI in MVP, industrial pilot or add-on phase?
- Is True Inventory needed for all categories or only fresh/problematic balance domains?
- What capacity limits are available as structured data: DC, transport, receiving, shelf workload?
