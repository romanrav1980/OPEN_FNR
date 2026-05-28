import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type ServiceLink = {
  name: string;
  url: string;
  purpose: string;
};

type DataLoadStatus = {
  domain: string;
  source: string;
  status: "loaded" | "partial" | "waiting";
  rows: string;
  cutoff: string;
};

type DataQualityIncident = {
  id: string;
  domain: string;
  severity: "blocker" | "warning";
  status: "blocking" | "in_review";
  affectedRows: string;
  owner: string;
  message: string;
};

type FeatureMartStatus = {
  version: string;
  status: "published" | "validated" | "failed";
  activePairs: string;
  features: number;
  quality: string;
};

const serviceLinks: ServiceLink[] = [
  { name: "API", url: "http://127.0.0.1:8000/docs", purpose: "OpenAPI" },
  { name: "Airflow", url: "http://127.0.0.1:18088", purpose: "Batch orchestration" },
  { name: "Flowable", url: "http://127.0.0.1:18080", purpose: "Process engine" },
  { name: "ClickHouse", url: "http://127.0.0.1:18123/play", purpose: "Forecast store" },
  { name: "OpenSearch", url: "http://127.0.0.1:15601", purpose: "Logs" },
  { name: "Superset", url: "http://127.0.0.1:18089", purpose: "BI" },
];

const dataLoadStatuses: DataLoadStatus[] = [
  { domain: "Sales", source: "POS", status: "loaded", rows: "1.25M", cutoff: "02:30" },
  { domain: "Stock", source: "WMS", status: "partial", rows: "1.19M", cutoff: "02:45" },
  { domain: "Prices", source: "ERP", status: "waiting", rows: "-", cutoff: "03:00" },
  { domain: "Product MDM", source: "MDM", status: "loaded", rows: "5.5K", cutoff: "01:30" },
  { domain: "Store MDM", source: "MDM", status: "loaded", rows: "30K", cutoff: "01:30" },
];

const dataQualityIncidents: DataQualityIncident[] = [
  {
    id: "dq-20260528-sales-001",
    domain: "Sales",
    severity: "blocker",
    status: "blocking",
    affectedRows: "128",
    owner: "Data Engineer",
    message: "Missing store_id in inbound sales rows.",
  },
  {
    id: "dq-20260528-prices-001",
    domain: "Prices",
    severity: "warning",
    status: "in_review",
    affectedRows: "5.4K",
    owner: "Data Owner",
    message: "Prices arrived after configured cutoff.",
  },
];

const featureMartStatuses: FeatureMartStatus[] = [
  { version: "fm-20260528-001", status: "published", activePairs: "2.14M", features: 42, quality: "accepted" },
  { version: "fm-20260528-002", status: "validated", activePairs: "0.82M", features: 42, quality: "pilot shard" },
  { version: "fm-20260528-003", status: "failed", activePairs: "0.31M", features: 39, quality: "partition error" },
];

const forecastRows = [
  { date: "2026-05-29", store: "S001", sku: "SKU001", regular: "12.4", total: "12.4", flag: "ok" },
  { date: "2026-05-29", store: "S001", sku: "SKU002", regular: "4.8", total: "4.8", flag: "low_history" },
];

const modelVersions = [
  {
    version: "lgbm-regular-v1-candidate",
    status: "backtested",
    algorithm: "LightGBM",
    wape: "15.8%",
    bias: "-0.6%",
    delta: "-2.6 pp",
    fallback: "seasonal-naive-v1",
  },
  {
    version: "seasonal-naive-v1",
    status: "promoted",
    algorithm: "Seasonal naive",
    wape: "18.4%",
    bias: "-1.2%",
    delta: "baseline",
    fallback: "-",
  },
];

const promoPlans = [
  {
    id: "promo-20260601-fresh-001",
    status: "ready_for_forecast",
    sku: "SKU001, SKU002",
    stores: "S001, S002",
    dates: "2026-06-01..2026-06-07",
    discount: "20%",
    price: "119.90",
    display: "End cap / 120 units",
  },
  {
    id: "promo-20260605-grocery-002",
    status: "conflict",
    sku: "SKU010",
    stores: "S001",
    dates: "2026-06-05..2026-06-12",
    discount: "11%",
    price: "79.90",
    display: "Island / 80 units",
  },
];

const promoForecastDays = [
  { date: "2026-06-01", regular: 120, uplift: 48, total: 168, stock: 340 },
  { date: "2026-06-02", regular: 118, uplift: 45, total: 163, stock: 290 },
];

const referencePromos = [
  { id: "promo-ref-202505-fresh-011", similarity: "0.91", discount: "20%", uplift: "42%" },
  { id: "promo-ref-202504-fresh-007", similarity: "0.84", discount: "18%", uplift: "37%" },
];

const processTasks = [
  {
    id: "task-promo-001",
    process: "promo_draft_validation_process",
    businessKey: "promo-20260605-grocery-002",
    name: "Resolve promo data issue",
    role: "Promo Planner",
    status: "open",
    sla: "12:00",
    actions: "complete / comment / escalate",
  },
  {
    id: "task-forecast-001",
    process: "forecast_review_process",
    businessKey: "regular-baseline-20260528-001",
    name: "Review forecast anomaly",
    role: "Forecast Planner",
    status: "open",
    sla: "15:00",
    actions: "accept / adjust / comment",
  },
  {
    id: "task-replenishment-001",
    process: "replenishment_approval_process",
    businessKey: "order-proposal-20260528-001",
    name: "Approve replenishment exception",
    role: "Replenishment Planner",
    status: "escalated",
    sla: "11:30",
    actions: "approve / reject / comment",
  },
];

const processHistory = [
  { time: "09:10", event: "process_started", actor: "Flowable", text: "Promo validation started" },
  { time: "09:15", event: "task_created", actor: "Flowable", text: "Task assigned to Promo Planner" },
  { time: "11:31", event: "sla_escalated", actor: "Flowable", text: "Replenishment task escalated" },
];

const promoApprovalSteps = [
  {
    step: "Category review",
    role: "Category Manager",
    status: "category_review",
    sla: "2026-05-29 09:00",
    actions: "approve / reject / request rework",
  },
  {
    step: "Supply review",
    role: "Supply Chain Manager",
    status: "supply_review",
    sla: "2026-05-28 17:00",
    actions: "approve / reject / request rework / escalate",
  },
];

const promoApprovalTimeline = [
  { time: "12:00", event: "approval_requested", actor: "Promo Planner", text: "Approval route requested" },
  { time: "12:10", event: "task_created", actor: "Flowable", text: "Category review task created" },
  { time: "12:20", event: "task_created", actor: "Flowable", text: "Supply review task created" },
];

const inventoryProjectionDays = [
  { date: "2026-05-29", opening: 200, demand: 52, openOrders: 0, inTransit: 0, projected: 148, risk: "none" },
  { date: "2026-05-30", opening: 148, demand: 65, openOrders: 80, inTransit: 0, projected: 163, risk: "none" },
  { date: "2026-05-31", opening: 163, demand: 88, openOrders: 0, inTransit: 60, projected: 135, risk: "none" },
  { date: "2026-06-01", opening: 135, demand: 168, openOrders: 0, inTransit: 0, projected: -33, risk: "stock_out" },
];

const orderProposals = [
  {
    id: "order-proposal-20260528-s001-sku001",
    status: "manual_review",
    sku: "SKU001",
    supplier: "SUP001",
    gross: 321,
    net: 273,
    raw: 273,
    rounded: 276,
    flags: "stock_out_risk, manual_review_required",
  },
  {
    id: "order-proposal-20260528-s001-sku002",
    status: "auto_approved",
    sku: "SKU002",
    supplier: "SUP001",
    gross: 42,
    net: 37,
    raw: 37,
    rounded: 48,
    flags: "rounded_to_order_multiple",
  },
  {
    id: "order-proposal-20260528-s001-sku003",
    status: "blocked",
    sku: "SKU003",
    supplier: "SUP002",
    gross: 120,
    net: 165,
    raw: 165,
    rounded: 168,
    flags: "supplier_blocked, calendar_closed",
  },
];

const finalOrders = [
  { id: "final-order-20260528-s001-sku001", proposal: "SKU001", status: "manual_review", proposed: 276, final: 276, impact: 243 },
  { id: "final-order-20260528-s001-sku002", proposal: "SKU002", status: "approved", proposed: 48, final: 48, impact: 103 },
];

const orderAudit = [
  { time: "05:10", actor: "Replenishment Planner", event: "approved", oldQty: 48, newQty: 48, reason: "auto approval accepted" },
  { time: "06:00", actor: "Replenishment Planner", event: "adjusted", oldQty: 276, newQty: 300, reason: "cover promo stock-out" },
];

const exceptionItems = [
  {
    id: "exc-stockout-20260528-001",
    type: "stock_out_risk",
    severity: "high",
    status: "new",
    owner: "Replenishment Planner",
    title: "Projected stock-out on promo start",
    action: "Raise final order before cutoff",
    linked: "projection-20260528-s001-sku001, order-proposal-20260528-s001-sku001",
  },
  {
    id: "exc-promo-shortage-20260528-001",
    type: "promo_shortage_risk",
    severity: "critical",
    status: "escalated",
    owner: "Supply Chain Manager",
    title: "Promo supply shortage risk",
    action: "Approve mitigation plan",
    linked: "promo-20260601-fresh-001",
  },
  {
    id: "exc-supplier-20260528-001",
    type: "supplier_constraint",
    severity: "medium",
    status: "in_review",
    owner: "Replenishment Planner",
    title: "Supplier calendar closed",
    action: "Find alternative supplier",
    linked: "order-proposal-20260528-s001-sku003",
  },
];

const exceptionAudit = [
  { time: "05:20", actor: "Replenishment Planner", action: "take", reason: "supplier calendar issue" },
  { time: "14:00", actor: "Replenishment Planner", action: "resolve", reason: "order adjusted" },
];

const manualAdjustments = [
  {
    id: "adj-forecast-20260528-001",
    target: "regular-baseline-20260528-001",
    type: "forecast",
    status: "previewed",
    mode: "percent",
    value: "+10%",
    reason: "local_event",
    validity: "2026-06-01..2026-06-07",
    effect: "120 -> 132",
  },
  {
    id: "adj-order-20260528-001",
    target: "order-proposal-20260528-s001-sku001",
    type: "order_proposal",
    status: "applied",
    mode: "absolute",
    value: "300",
    reason: "supply_constraint",
    validity: "2026-05-30",
    effect: "276 -> 300",
  },
];

const adjustmentAudit = [
  { time: "15:00", actor: "Forecast Planner", action: "preview", oldValue: 120, newValue: 132, reason: "local_event" },
  { time: "06:10", actor: "Replenishment Planner", action: "apply", oldValue: 276, newValue: 300, reason: "supply_constraint" },
];

const publicationPackages = [
  {
    id: "pub-wms-orders-20260528-001",
    target: "wms",
    status: "prepared",
    key: "wms:orders:20260528:001",
    object: "final-order-20260528-s001-sku002",
    response: "-",
    retry: 0,
    exception: "-",
  },
  {
    id: "pub-dwh-forecast-20260528-001",
    target: "dwh",
    status: "accepted",
    key: "dwh:forecast:20260528:001",
    object: "regular-baseline-20260528-001",
    response: "200 accepted",
    retry: 0,
    exception: "-",
  },
  {
    id: "pub-erp-orders-20260528-001",
    target: "erp",
    status: "failed",
    key: "erp:orders:20260528:001",
    object: "final-order-20260528-s001-sku003",
    response: "ERP_TIMEOUT",
    retry: 1,
    exception: "exc-export-20260528-001",
  },
  {
    id: "pub-wms-orders-20260528-002",
    target: "wms",
    status: "rejected",
    key: "wms:orders:20260528:002",
    object: "final-order-20260528-s001-sku001",
    response: "NOT_APPROVED",
    retry: 0,
    exception: "-",
  },
];

const publicationAudit = [
  { time: "05:40", target: "dwh", event: "accepted", key: "dwh:forecast:20260528:001", response: "200 accepted" },
  { time: "06:40", target: "erp", event: "failed", key: "erp:orders:20260528:001", response: "ERP_TIMEOUT" },
  { time: "07:05", target: "erp", event: "retry_sent", key: "erp:orders:20260528:001", response: "202 retry sent" },
];

const kpiRows = [
  {
    segment: "Network",
    status: "calculated",
    wape: "15.8%",
    bias: "-0.6%",
    service: "96.5%",
    oos: "2.1%",
    overstock: "1.42M",
    lostSales: "680K",
    waste: "210K",
    acceptance: "87%",
  },
  {
    segment: "North / fresh",
    status: "review_required",
    wape: "22.6%",
    bias: "-4.2%",
    service: "91.8%",
    oos: "5.7%",
    overstock: "210K",
    lostSales: "180K",
    waste: "65K",
    acceptance: "71%",
  },
  {
    segment: "S001 / SKU001",
    status: "action_created",
    wape: "24.1%",
    bias: "-4.4%",
    service: "90.2%",
    oos: "8.3%",
    overstock: "0",
    lostSales: "18K",
    waste: "0",
    acceptance: "67%",
  },
];

const freshBatches = [
  { batch: "batch-s001-sku001-001", received: "2026-05-26", expires: "2026-05-30", qty: 42, shelfLife: 2 },
  { batch: "batch-s001-sku001-002", received: "2026-05-27", expires: "2026-06-01", qty: 58, shelfLife: 4 },
];

const freshProjection = [
  { date: "2026-05-29", demand: 38, available: 100, waste: 0, service: "98%" },
  { date: "2026-05-30", demand: 44, available: 62, waste: 18, service: "97%" },
  { date: "2026-05-31", demand: 48, available: 38, waste: 16, service: "95%" },
];

const lifecycleRows = [
  {
    sku: "SKU_NEW_001",
    status: "planned",
    launch: "2026-06-10",
    termination: "-",
    reference: "SKU001",
    replacement: "-",
    forecast: "12.4",
    stock: "0",
    risk: "low",
  },
  {
    sku: "SKU_OLD_001",
    status: "phase_out",
    launch: "2024-01-15",
    termination: "2026-06-05",
    reference: "-",
    replacement: "SKU_NEW_001",
    forecast: "0",
    stock: "420",
    risk: "high",
  },
];

const dcPlanRows = [
  {
    plan: "dc-plan-20260528-dc001-sku001",
    dc: "DC001",
    region: "north",
    sku: "SKU001",
    status: "shortage",
    demand: 270,
    available: 210,
    shortage: 60,
    cutoff: "16:00",
    rule: "priority_service_risk_first",
  },
];

const dcAllocationRows = [
  {
    store: "S001",
    priority: "high",
    serviceRisk: "0.91",
    requested: 120,
    allocated: 120,
    unfilled: 0,
    reason: "priority and service risk covered",
  },
  {
    store: "S002",
    priority: "medium",
    serviceRisk: "0.63",
    requested: 90,
    allocated: 90,
    unfilled: 0,
    reason: "priority and service risk covered",
  },
  {
    store: "S003",
    priority: "low",
    serviceRisk: "0.28",
    requested: 60,
    allocated: 0,
    unfilled: 60,
    reason: "DC shortage after higher priority allocation",
  },
];

const performanceMetrics = [
  { metric: "Batch runtime", value: "76", threshold: "120", unit: "minutes", status: "passed" },
  { metric: "API p95 latency", value: "180", threshold: "500", unit: "ms", status: "passed" },
  { metric: "UI LCP", value: "2100", threshold: "3000", unit: "ms", status: "passed" },
  { metric: "ClickHouse read", value: "640", threshold: "1000", unit: "ms", status: "passed" },
  { metric: "Airflow DAG runtime", value: "84", threshold: "120", unit: "minutes", status: "passed" },
];

const performanceBottlenecks = [
  {
    component: "Spark feature build",
    severity: "medium",
    finding: "Feature join dominates pilot runtime.",
    recommendation: "Pre-partition sales and stock features by date, dc_id and category_id.",
  },
  {
    component: "ClickHouse dashboard reads",
    severity: "low",
    finding: "KPI dashboard uses repeated segment scans.",
    recommendation: "Add daily aggregate projection for WAPE and service-level slices.",
  },
];

function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Sprint 0</p>
          <h1>OPEN FNR Dev Control Tower</h1>
        </div>
        <span className="status-pill">Dev bootstrap</span>
      </header>

      <section className="summary-grid" aria-label="Project modules">
        <article>
          <span>Forecasting</span>
          <strong>Regular + promo uplift</strong>
        </article>
        <article>
          <span>Replenishment</span>
          <strong>Projected stock + orders</strong>
        </article>
        <article>
          <span>Process</span>
          <strong>BPMN / DMN / CMMN</strong>
        </article>
      </section>

      <section className="service-section">
        <div className="section-heading">
          <h2>Dev Services</h2>
          <p>Локальные сервисы разработки</p>
        </div>
        <div className="service-grid">
          {serviceLinks.map((service) => (
            <a className="service-card" href={service.url} key={service.name} target="_blank" rel="noreferrer">
              <span>{service.purpose}</span>
              <strong>{service.name}</strong>
            </a>
          ))}
        </div>
      </section>

      <section className="data-section" aria-label="Data load status">
        <div className="section-heading">
          <h2>Data Load Status</h2>
          <p>Read-only Sprint 1 view</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Domain</th>
                <th>Source</th>
                <th>Status</th>
                <th>Rows</th>
                <th>Cutoff</th>
              </tr>
            </thead>
            <tbody>
              {dataLoadStatuses.map((item) => (
                <tr key={item.domain}>
                  <td>{item.domain}</td>
                  <td>{item.source}</td>
                  <td>
                    <span className={`status-dot status-${item.status}`}>{item.status}</span>
                  </td>
                  <td>{item.rows}</td>
                  <td>{item.cutoff}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Data quality console">
        <div className="section-heading">
          <h2>Data Quality Console</h2>
          <p>Blocking incidents, waivers and re-checks</p>
        </div>
        <div className="dq-layout">
          <div className="dq-list">
            {dataQualityIncidents.map((incident) => (
              <article className="dq-card" key={incident.id}>
                <div>
                  <span className={`status-dot severity-${incident.severity}`}>{incident.severity}</span>
                  <span className="dq-domain">{incident.domain}</span>
                </div>
                <strong>{incident.id}</strong>
                <p>{incident.message}</p>
                <dl>
                  <div>
                    <dt>Status</dt>
                    <dd>{incident.status}</dd>
                  </div>
                  <div>
                    <dt>Rows</dt>
                    <dd>{incident.affectedRows}</dd>
                  </div>
                  <div>
                    <dt>Owner</dt>
                    <dd>{incident.owner}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
          <aside className="dq-detail">
            <span className="eyebrow">Selected Incident</span>
            <h3>Waiver requires Data Owner or Admin</h3>
            <p>
              Blocking DQ incidents stop publication until source data is fixed,
              checks are re-run or an audited waiver is approved.
            </p>
            <div className="action-row">
              <button type="button">Re-run</button>
              <button type="button">Waive</button>
              <button type="button">Export rows</button>
            </div>
          </aside>
        </div>
      </section>

      <section className="data-section" aria-label="Feature mart status">
        <div className="section-heading">
          <h2>Feature Mart Status</h2>
          <p>Active matrix and point-in-time features</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Active Matrix</span>
            <strong>2.14M store x SKU pairs</strong>
            <p>Closed stores, inactive SKU and invalid assortment pairs are excluded before feature build.</p>
          </article>
          <article className="feature-summary">
            <span>Feature Groups</span>
            <strong>Lag / rolling / price / stock</strong>
            <p>All registered features are marked as point-in-time safe for baseline forecasting.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Version</th>
                <th>Status</th>
                <th>Active Pairs</th>
                <th>Features</th>
                <th>Quality</th>
              </tr>
            </thead>
            <tbody>
              {featureMartStatuses.map((item) => (
                <tr key={item.version}>
                  <td>{item.version}</td>
                  <td>
                    <span className={`status-dot feature-${item.status}`}>{item.status}</span>
                  </td>
                  <td>{item.activePairs}</td>
                  <td>{item.features}</td>
                  <td>{item.quality}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Forecast baseline">
        <div className="section-heading">
          <h2>Forecast Workbench</h2>
          <p>Latest published seasonal naive forecast</p>
        </div>
        <div className="filter-bar" aria-label="Forecast filters">
          <label>
            Date
            <input value="2026-05-29" readOnly />
          </label>
          <label>
            Store
            <input value="S001" readOnly />
          </label>
          <label>
            SKU
            <input value="All" readOnly />
          </label>
          <label>
            Category
            <input value="fresh" readOnly />
          </label>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Version</span>
            <strong>regular-baseline-20260528-001</strong>
            <p>Model seasonal-naive-v1, feature version fm-20260528-001, horizon 30 days.</p>
          </article>
          <article className="feature-summary">
            <span>Quality</span>
            <strong>WAPE 18.4% / Bias -1.2%</strong>
            <p>Baseline is published and available for read-only review before ML model replacement.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="Fact vs forecast chart">
          <div className="chart-bars">
            <span style={{ height: "74%" }} title="Actual SKU001" />
            <span style={{ height: "84%" }} title="Forecast SKU001" />
            <span style={{ height: "38%" }} title="Actual SKU002" />
            <span style={{ height: "33%" }} title="Forecast SKU002" />
          </div>
          <p>Fact vs forecast, selected slice</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Store</th>
                <th>SKU</th>
                <th>Regular</th>
                <th>Total</th>
                <th>Flag</th>
              </tr>
            </thead>
            <tbody>
              {forecastRows.map((row) => (
                <tr key={`${row.date}-${row.store}-${row.sku}`}>
                  <td>{row.date}</td>
                  <td>{row.store}</td>
                  <td>{row.sku}</td>
                  <td>{row.regular}</td>
                  <td>{row.total}</td>
                  <td>{row.flag}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Model monitoring">
        <div className="section-heading">
          <h2>Model Monitoring V1</h2>
          <p>ML candidate vs baseline, approval and fallback</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Candidate</span>
            <strong>lgbm-regular-v1-candidate</strong>
            <p>Backtested on feature version fm-20260528-001 and ready for Forecast Owner review.</p>
          </article>
          <article className="feature-summary">
            <span>Approval Gate</span>
            <strong>WAPE improved / Bias within threshold</strong>
            <p>Promotion requires Forecast Owner or ML Owner approval and keeps baseline fallback active.</p>
          </article>
        </div>
        <div className="model-actions" aria-label="Model approval actions">
          <button type="button">Approve</button>
          <button type="button">Reject</button>
          <button type="button">Activate fallback</button>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Status</th>
                <th>Algorithm</th>
                <th>WAPE</th>
                <th>Bias</th>
                <th>Delta</th>
                <th>Fallback</th>
              </tr>
            </thead>
            <tbody>
              {modelVersions.map((model) => (
                <tr key={model.version}>
                  <td>{model.version}</td>
                  <td>{model.status}</td>
                  <td>{model.algorithm}</td>
                  <td>{model.wape}</td>
                  <td>{model.bias}</td>
                  <td>{model.delta}</td>
                  <td>{model.fallback}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Promo workbench">
        <div className="section-heading">
          <h2>Promo Workbench Draft</h2>
          <p>Mandatory fields, display capacity and overlap validation</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Required Promo Fields</span>
            <strong>SKU / stores / dates / price / discount / display</strong>
            <p>Promo cannot move to forecast until required commercial and display attributes are complete.</p>
          </article>
          <article className="feature-summary">
            <span>Validation Process</span>
            <strong>Completeness + overlap checks</strong>
            <p>Conflicts create a promo data issue case for Promo Planner and Category Manager.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Promo</th>
                <th>Status</th>
                <th>SKU</th>
                <th>Stores</th>
                <th>Dates</th>
                <th>Discount</th>
                <th>Price</th>
                <th>Display</th>
              </tr>
            </thead>
            <tbody>
              {promoPlans.map((promo) => (
                <tr key={promo.id}>
                  <td>{promo.id}</td>
                  <td>{promo.status}</td>
                  <td>{promo.sku}</td>
                  <td>{promo.stores}</td>
                  <td>{promo.dates}</td>
                  <td>{promo.discount}</td>
                  <td>{promo.price}</td>
                  <td>{promo.display}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Promo forecast">
        <div className="section-heading">
          <h2>Promo Forecast V1</h2>
          <p>Regular baseline + promo uplift = total forecast</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Promo Forecast</span>
            <strong>promo-20260601-fresh-001</strong>
            <p>Uplift version promo-uplift-v1-20260528, status forecasted, accuracy smoke 82%.</p>
          </article>
          <article className="feature-summary">
            <span>Post-promo Stock</span>
            <strong>340 -&gt; 290 units</strong>
            <p>Preview helps replenishment see stock pressure after promo demand uplift.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="Promo regular uplift total chart">
          <div className="chart-bars">
            <span style={{ height: "62%" }} title="Regular day 1" />
            <span style={{ height: "25%" }} title="Uplift day 1" />
            <span style={{ height: "88%" }} title="Total day 1" />
            <span style={{ height: "61%" }} title="Regular day 2" />
            <span style={{ height: "23%" }} title="Uplift day 2" />
            <span style={{ height: "85%" }} title="Total day 2" />
          </div>
          <p>Regular, uplift and total demand curve for promo period</p>
        </div>
        <div className="feature-grid">
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Regular</th>
                  <th>Uplift</th>
                  <th>Total</th>
                  <th>Post-stock</th>
                </tr>
              </thead>
              <tbody>
                {promoForecastDays.map((day) => (
                  <tr key={day.date}>
                    <td>{day.date}</td>
                    <td>{day.regular}</td>
                    <td>{day.uplift}</td>
                    <td>{day.total}</td>
                    <td>{day.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Reference promo</th>
                  <th>Similarity</th>
                  <th>Discount</th>
                  <th>Uplift</th>
                </tr>
              </thead>
              <tbody>
                {referencePromos.map((promo) => (
                  <tr key={promo.id}>
                    <td>{promo.id}</td>
                    <td>{promo.similarity}</td>
                    <td>{promo.discount}</td>
                    <td>{promo.uplift}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Process engine task inbox">
        <div className="section-heading">
          <h2>Process Engine Task Inbox</h2>
          <p>BPMN / DMN / CMMN tasks, actions and audit trail</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Deployment</span>
            <strong>Flowable OSS process layer</strong>
            <p>Definitions are versioned and deployed through backend contracts, with task transitions coming from process metadata.</p>
          </article>
          <article className="feature-summary">
            <span>RBAC</span>
            <strong>Role-based task visibility</strong>
            <p>Promo, forecast and replenishment tasks are visible only to assigned or candidate roles, with Admin audit access.</p>
          </article>
        </div>
        <div className="filter-bar" aria-label="Process filters">
          <label>
            Role
            <input value="Promo Planner" readOnly />
          </label>
          <label>
            Status
            <input value="Open + escalated" readOnly />
          </label>
          <label>
            Process
            <input value="All deployed" readOnly />
          </label>
          <label>
            SLA
            <input value="Due today" readOnly />
          </label>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Task</th>
                <th>Process</th>
                <th>Business key</th>
                <th>Role</th>
                <th>Status</th>
                <th>SLA</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {processTasks.map((task) => (
                <tr key={task.id}>
                  <td>{task.name}</td>
                  <td>{task.process}</td>
                  <td>{task.businessKey}</td>
                  <td>{task.role}</td>
                  <td>{task.status}</td>
                  <td>{task.sla}</td>
                  <td>{task.actions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Selected Task</span>
            <h3>Resolve promo data issue</h3>
            <p>
              The user reviews the process-generated task, adds a comment, completes the action,
              and the backend writes comment and completion events to audit history.
            </p>
            <div className="action-row">
              <button type="button">Complete</button>
              <button type="button">Comment</button>
              <button type="button">Escalate</button>
            </div>
          </aside>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>Actor</th>
                  <th>Audit message</th>
                </tr>
              </thead>
              <tbody>
                {processHistory.map((event) => (
                  <tr key={`${event.time}-${event.event}`}>
                    <td>{event.time}</td>
                    <td>{event.event}</td>
                    <td>{event.actor}</td>
                    <td>{event.text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Promo approval process">
        <div className="section-heading">
          <h2>Promo Approval Process</h2>
          <p>Category and supply approvals with risk route, rework and rejection paths</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Promo</span>
            <strong>promo-20260601-fresh-001</strong>
            <p>Status category_review, process instance proc-promo-approval-20260601-001.</p>
          </article>
          <article className="feature-summary">
            <span>Risk</span>
            <strong>Medium</strong>
            <p>Risk reasons: discount over 15%, post-promo stock remains above safety threshold.</p>
          </article>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Decision Panel</span>
            <h3>Category Manager approval</h3>
            <p>
              Decision buttons are provided by the process task. Every decision requires a user,
              comment and reason before the promo can move to supply review or return to rework.
            </p>
            <div className="action-row">
              <button type="button">Approve</button>
              <button type="button">Reject</button>
              <button type="button">Request rework</button>
              <button type="button">Comment</button>
            </div>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Blocking Errors</span>
            <h3>No blockers for selected promo</h3>
            <p>
              A conflicting promo would block publication and create a rework task for Promo Planner
              until SKU, dates, price or display capacity are fixed.
            </p>
          </aside>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Step</th>
                <th>Role</th>
                <th>Status</th>
                <th>SLA</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {promoApprovalSteps.map((step) => (
                <tr key={step.step}>
                  <td>{step.step}</td>
                  <td>{step.role}</td>
                  <td>{step.status}</td>
                  <td>{step.sla}</td>
                  <td>{step.actions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Event</th>
                <th>Actor</th>
                <th>Timeline</th>
              </tr>
            </thead>
            <tbody>
              {promoApprovalTimeline.map((event) => (
                <tr key={`${event.time}-${event.event}`}>
                  <td>{event.time}</td>
                  <td>{event.event}</td>
                  <td>{event.actor}</td>
                  <td>{event.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Inventory projection">
        <div className="section-heading">
          <h2>Inventory Projection</h2>
          <p>Projected stock, demand projection, open orders, in-transit and safety threshold</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Projection</span>
            <strong>projection-20260528-s001-sku001</strong>
            <p>Store S001, SKU001, forecast regular-baseline-20260528-001, lead time 2 days.</p>
          </article>
          <article className="feature-summary">
            <span>Stock-out Warning</span>
            <strong>2026-06-01 projected stock -33</strong>
            <p>Demand projection consumes available stock before additional receipts are planned.</p>
          </article>
        </div>
        <div className="filter-bar" aria-label="Inventory projection filters">
          <label>
            Store
            <input value="S001" readOnly />
          </label>
          <label>
            SKU
            <input value="SKU001" readOnly />
          </label>
          <label>
            Horizon
            <input value="4 days" readOnly />
          </label>
          <label>
            Safety
            <input value="90 units" readOnly />
          </label>
        </div>
        <div className="chart-panel" aria-label="Projected stock graph">
          <div className="chart-bars projection-bars">
            <span style={{ height: "72%" }} title="Projected stock day 1" />
            <span style={{ height: "79%" }} title="Projected stock day 2" />
            <span style={{ height: "66%" }} title="Projected stock day 3" />
            <span style={{ height: "12%" }} title="Projected stock day 4 stock-out" />
          </div>
          <p>Projected stock with safety threshold 90 units; day 4 is below zero and requires planner review.</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Opening</th>
                <th>Demand</th>
                <th>Open orders</th>
                <th>In-transit</th>
                <th>Projected</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {inventoryProjectionDays.map((day) => (
                <tr key={day.date}>
                  <td>{day.date}</td>
                  <td>{day.opening}</td>
                  <td>{day.demand}</td>
                  <td>{day.openOrders}</td>
                  <td>{day.inTransit}</td>
                  <td>{day.projected}</td>
                  <td>{day.risk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="data-section" aria-label="Order proposals">
        <div className="section-heading">
          <h2>Order Proposal V1</h2>
          <p>Explainable order quantity with net requirement, MOQ, rounding and constraints</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Selected Proposal</span>
            <strong>order-proposal-20260528-s001-sku001</strong>
            <p>Manual review because the projection has stock-out risk during promo demand.</p>
          </article>
          <article className="feature-summary">
            <span>Formula</span>
            <strong>321 + 90 + 25 - 163 = 273 raw</strong>
            <p>Rounded to 276 by MOQ 24 and order multiple 12 before planner approval.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Proposal</th>
                <th>Status</th>
                <th>SKU</th>
                <th>Supplier</th>
                <th>Gross</th>
                <th>Net</th>
                <th>Raw</th>
                <th>Rounded</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {orderProposals.map((proposal) => (
                <tr key={proposal.id}>
                  <td>{proposal.id}</td>
                  <td>{proposal.status}</td>
                  <td>{proposal.sku}</td>
                  <td>{proposal.supplier}</td>
                  <td>{proposal.gross}</td>
                  <td>{proposal.net}</td>
                  <td>{proposal.raw}</td>
                  <td>{proposal.rounded}</td>
                  <td>{proposal.flags}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Explanation Drawer</span>
            <h3>Why 276 units?</h3>
            <p>
              Gross requirement 321 plus safety stock 90 and presentation stock 25,
              minus projected stock at receipt 163, gives net requirement 273.
              Order multiple 12 rounds it to 276.
            </p>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Constraint Flags</span>
            <h3>Manual review required</h3>
            <p>
              The order is explainable and not blocked, but stock-out risk requires
              Replenishment Planner review before publication.
            </p>
            <div className="action-row">
              <button type="button">Approve</button>
              <button type="button">Adjust</button>
              <button type="button">Block</button>
            </div>
          </aside>
        </div>
      </section>

      <section className="data-section" aria-label="Replenishment workbench">
        <div className="section-heading">
          <h2>Replenishment Workbench</h2>
          <p>Planner workspace for final order review, adjustment, approval and audit</p>
        </div>
        <div className="filter-bar" aria-label="Replenishment workbench filters">
          <label>
            Supplier
            <input value="SUP001" readOnly />
          </label>
          <label>
            DC
            <input value="DC001" readOnly />
          </label>
          <label>
            Store
            <input value="S001" readOnly />
          </label>
          <label>
            Category
            <input value="fresh" readOnly />
          </label>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Mass Action</span>
            <strong>1 auto-approved order ready</strong>
            <p>Mass approval prepares async export only for approved final orders.</p>
          </article>
          <article className="feature-summary">
            <span>Preview Impact</span>
            <strong>-33 + 300 = 267 projected stock</strong>
            <p>Manual adjustment keeps the original proposal and writes old/new quantities to audit.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Final order</th>
                <th>SKU</th>
                <th>Status</th>
                <th>Proposed</th>
                <th>Final</th>
                <th>Projected after order</th>
              </tr>
            </thead>
            <tbody>
              {finalOrders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{order.proposal}</td>
                  <td>{order.status}</td>
                  <td>{order.proposed}</td>
                  <td>{order.final}</td>
                  <td>{order.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Adjustment Modal</span>
            <h3>Change final order to 300</h3>
            <p>
              Planner enters final quantity, reason and comment. The proposal quantity remains unchanged,
              while the final order and projected stock impact are recalculated.
            </p>
            <div className="action-row">
              <button type="button">Preview</button>
              <button type="button">Approve</button>
              <button type="button">Reject</button>
              <button type="button">Escalate</button>
            </div>
          </aside>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Actor</th>
                  <th>Event</th>
                  <th>Old</th>
                  <th>New</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {orderAudit.map((event) => (
                  <tr key={`${event.time}-${event.event}`}>
                    <td>{event.time}</td>
                    <td>{event.actor}</td>
                    <td>{event.event}</td>
                    <td>{event.oldQty}</td>
                    <td>{event.newQty}</td>
                    <td>{event.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Exception center">
        <div className="section-heading">
          <h2>Exception Center</h2>
          <p>Unified exception workspace with owners, SLA, linked objects and audited actions</p>
        </div>
        <div className="filter-bar" aria-label="Exception filters">
          <label>
            Type
            <input value="All risks" readOnly />
          </label>
          <label>
            Severity
            <input value="Critical + high" readOnly />
          </label>
          <label>
            Owner
            <input value="My teams" readOnly />
          </label>
          <label>
            Status
            <input value="New + in review + escalated" readOnly />
          </label>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Selected Exception</span>
            <strong>Projected stock-out on promo start</strong>
            <p>Owner Replenishment Planner, SLA 2026-05-28 14:30, linked to projection and order proposal.</p>
          </article>
          <article className="feature-summary">
            <span>Recommended Action</span>
            <strong>Raise final order before cutoff</strong>
            <p>Resolving this exception requires an audited comment and linked final order change.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Exception</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Owner</th>
                <th>Recommended action</th>
                <th>Linked objects</th>
              </tr>
            </thead>
            <tbody>
              {exceptionItems.map((item) => (
                <tr key={item.id}>
                  <td>{item.title}</td>
                  <td>{item.type}</td>
                  <td>{item.severity}</td>
                  <td>{item.status}</td>
                  <td>{item.owner}</td>
                  <td>{item.action}</td>
                  <td>{item.linked}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Action Panel</span>
            <h3>Resolve stock-out exception</h3>
            <p>
              The owner can take, resolve, ignore or escalate an exception. Every action
              requires a reason and comment, and creates an audit event.
            </p>
            <div className="action-row">
              <button type="button">Take</button>
              <button type="button">Resolve</button>
              <button type="button">Ignore</button>
              <button type="button">Escalate</button>
            </div>
          </aside>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {exceptionAudit.map((event) => (
                  <tr key={`${event.time}-${event.action}`}>
                    <td>{event.time}</td>
                    <td>{event.actor}</td>
                    <td>{event.action}</td>
                    <td>{event.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Manual adjustments">
        <div className="section-heading">
          <h2>Manual Adjustments</h2>
          <p>Safe overlay for forecast, promo and order changes with preview, validity and audit</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Adjustment Modal</span>
            <strong>Raise forecast by 10%</strong>
            <p>Reason local_event is required. Scope: S001/S002, SKU001/SKU002, 2026-06-01..2026-06-07.</p>
          </article>
          <article className="feature-summary">
            <span>Impact Preview</span>
            <strong>120 -&gt; 132, 4 rows affected</strong>
            <p>Original ML forecast remains unchanged; adjustment is applied as an overlay before publication.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Adjustment</th>
                <th>Target</th>
                <th>Type</th>
                <th>Status</th>
                <th>Mode</th>
                <th>Value</th>
                <th>Reason</th>
                <th>Validity</th>
                <th>Effect</th>
              </tr>
            </thead>
            <tbody>
              {manualAdjustments.map((adjustment) => (
                <tr key={adjustment.id}>
                  <td>{adjustment.id}</td>
                  <td>{adjustment.target}</td>
                  <td>{adjustment.type}</td>
                  <td>{adjustment.status}</td>
                  <td>{adjustment.mode}</td>
                  <td>{adjustment.value}</td>
                  <td>{adjustment.reason}</td>
                  <td>{adjustment.validity}</td>
                  <td>{adjustment.effect}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Actions</span>
            <h3>Preview, apply or cancel</h3>
            <p>
              A planner can preview the effect, request approval when thresholds are exceeded,
              apply the overlay, or cancel it before publication cutoff.
            </p>
            <div className="action-row">
              <button type="button">Preview</button>
              <button type="button">Approve</button>
              <button type="button">Apply</button>
              <button type="button">Cancel</button>
            </div>
          </aside>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Old</th>
                  <th>New</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {adjustmentAudit.map((event) => (
                  <tr key={`${event.time}-${event.action}`}>
                    <td>{event.time}</td>
                    <td>{event.actor}</td>
                    <td>{event.action}</td>
                    <td>{event.oldValue}</td>
                    <td>{event.newValue}</td>
                    <td>{event.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Publication console">
        <div className="section-heading">
          <h2>Publication Console</h2>
          <p>Controlled export of forecasts and orders with idempotency, retry and audit</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Ready Package</span>
            <strong>pub-wms-orders-20260528-001</strong>
            <p>Final order export to WMS mock uses idempotency key wms:orders:20260528:001.</p>
          </article>
          <article className="feature-summary">
            <span>Failed Export</span>
            <strong>ERP_TIMEOUT linked to exc-export-20260528-001</strong>
            <p>Failure opens export failure case and allows controlled retry by Integration Owner.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Package</th>
                <th>Target</th>
                <th>Status</th>
                <th>Idempotency key</th>
                <th>Object</th>
                <th>Response</th>
                <th>Retry</th>
                <th>Exception</th>
              </tr>
            </thead>
            <tbody>
              {publicationPackages.map((pkg) => (
                <tr key={pkg.id}>
                  <td>{pkg.id}</td>
                  <td>{pkg.target}</td>
                  <td>{pkg.status}</td>
                  <td>{pkg.key}</td>
                  <td>{pkg.object}</td>
                  <td>{pkg.response}</td>
                  <td>{pkg.retry}</td>
                  <td>{pkg.exception}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Retry Action</span>
            <h3>Retry failed ERP export</h3>
            <p>
              Retry keeps the same idempotency key, increments retry count, and stores target
              response for audit. Unapproved final orders are rejected before send.
            </p>
            <div className="action-row">
              <button type="button">Send</button>
              <button type="button">Retry</button>
              <button type="button">Open exception</button>
            </div>
          </aside>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Target</th>
                  <th>Event</th>
                  <th>Key</th>
                  <th>Response</th>
                </tr>
              </thead>
              <tbody>
                {publicationAudit.map((event) => (
                  <tr key={`${event.time}-${event.event}`}>
                    <td>{event.time}</td>
                    <td>{event.target}</td>
                    <td>{event.event}</td>
                    <td>{event.key}</td>
                    <td>{event.response}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="Accuracy and KPI dashboard">
        <div className="section-heading">
          <h2>Accuracy And KPI Dashboard</h2>
          <p>Forecast accuracy, replenishment impact and business value drill-down</p>
        </div>
        <div className="filter-bar" aria-label="KPI filters">
          <label>
            Network
            <input value="OPEN_FNR_NETWORK" readOnly />
          </label>
          <label>
            Region
            <input value="north" readOnly />
          </label>
          <label>
            Category
            <input value="fresh" readOnly />
          </label>
          <label>
            SKU
            <input value="SKU001 drill-down" readOnly />
          </label>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Accuracy</span>
            <strong>WAPE 15.8% / Bias -0.6%</strong>
            <p>Network level is within threshold, while North fresh requires review due to WAPE and service level.</p>
          </article>
          <article className="feature-summary">
            <span>Business Value Draft</span>
            <strong>Service + stock + lost sales + waste</strong>
            <p>Dashboard connects forecast quality to service level, lost sales, overstock and waste impact.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="KPI trend chart">
          <div className="chart-bars">
            <span style={{ height: "58%" }} title="Network WAPE" />
            <span style={{ height: "80%" }} title="North fresh WAPE" />
            <span style={{ height: "86%" }} title="SKU WAPE" />
            <span style={{ height: "65%" }} title="Service impact" />
          </div>
          <p>Trend visual: network WAPE, segment WAPE, SKU WAPE and service impact alert.</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Segment</th>
                <th>Status</th>
                <th>WAPE</th>
                <th>Bias</th>
                <th>Service</th>
                <th>OOS</th>
                <th>Overstock</th>
                <th>Lost sales</th>
                <th>Waste</th>
                <th>Proposal acceptance</th>
              </tr>
            </thead>
            <tbody>
              {kpiRows.map((row) => (
                <tr key={row.segment}>
                  <td>{row.segment}</td>
                  <td>{row.status}</td>
                  <td>{row.wape}</td>
                  <td>{row.bias}</td>
                  <td>{row.service}</td>
                  <td>{row.oos}</td>
                  <td>{row.overstock}</td>
                  <td>{row.lostSales}</td>
                  <td>{row.waste}</td>
                  <td>{row.acceptance}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Review Task</span>
            <h3>North fresh KPI degradation</h3>
            <p>
              KPI alert decision creates weekly review when WAPE is above 20%,
              absolute bias is above 5%, or service level is below 94%.
            </p>
            <div className="action-row">
              <button type="button">Open review</button>
              <button type="button">Create action</button>
              <button type="button">Mark reviewed</button>
            </div>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Drill-down</span>
            <h3>S001 / SKU001</h3>
            <p>
              SKU view compares ML forecast and final forecast, showing manual adjustment effect
              and whether proposal acceptance improved replenishment outcomes.
            </p>
          </aside>
        </div>
      </section>

      <section className="data-section" aria-label="Fresh workbench">
        <div className="section-heading">
          <h2>Fresh Workbench</h2>
          <p>Shelf-life, FEFO batches, expected waste and availability-vs-waste preview</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Fresh SKU</span>
            <strong>S001 / SKU001 spoilage risk high</strong>
            <p>Recommended order 96 adjusted to 72 to reduce projected waste before fresh cutoff.</p>
          </article>
          <article className="feature-summary">
            <span>Waste-Service Trade-off</span>
            <strong>Waste 34 -&gt; 14, service 97% -&gt; 95%</strong>
            <p>Fresh Manager approves lower waste while keeping service above the configured threshold.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="Expected waste graph">
          <div className="chart-bars">
            <span style={{ height: "12%" }} title="Waste day 1" />
            <span style={{ height: "54%" }} title="Waste day 2" />
            <span style={{ height: "48%" }} title="Waste day 3" />
            <span style={{ height: "42%" }} title="Waste after adjustment" />
          </div>
          <p>Expected waste before/after fresh order adjustment with service-level preview.</p>
        </div>
        <div className="feature-grid">
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Batch</th>
                  <th>Received</th>
                  <th>Expires</th>
                  <th>Qty</th>
                  <th>Shelf-life days</th>
                </tr>
              </thead>
              <tbody>
                {freshBatches.map((batch) => (
                  <tr key={batch.batch}>
                    <td>{batch.batch}</td>
                    <td>{batch.received}</td>
                    <td>{batch.expires}</td>
                    <td>{batch.qty}</td>
                    <td>{batch.shelfLife}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Demand</th>
                  <th>Available</th>
                  <th>Waste</th>
                  <th>Service</th>
                </tr>
              </thead>
              <tbody>
                {freshProjection.map((day) => (
                  <tr key={day.date}>
                    <td>{day.date}</td>
                    <td>{day.demand}</td>
                    <td>{day.available}</td>
                    <td>{day.waste}</td>
                    <td>{day.service}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="dq-detail">
          <span className="eyebrow">Fresh Adjustment</span>
          <h3>Reduce order 96 to 72</h3>
          <p>
            FEFO batches with the nearest expiration are consumed first. High spoilage risk opens
            a case where Fresh Manager reviews expected waste and approves the service trade-off.
          </p>
          <div className="action-row">
            <button type="button">Review</button>
            <button type="button">Adjust</button>
            <button type="button">Approve</button>
          </div>
        </div>
      </section>

      <section className="data-section" aria-label="SKU lifecycle">
        <div className="section-heading">
          <h2>SKU Lifecycle</h2>
          <p>Phase-in, reference product, phase-out, termination and clearance risk</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Phase-in</span>
            <strong>SKU_NEW_001 uses SKU001 as reference</strong>
            <p>Cold-start forecast 12.4 is generated before launch date and active matrix update.</p>
          </article>
          <article className="feature-summary">
            <span>Phase-out</span>
            <strong>SKU_OLD_001 terminates on 2026-06-05</strong>
            <p>Replacement SKU_NEW_001 is linked. Orders after termination date are blocked.</p>
          </article>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Status</th>
                <th>Launch</th>
                <th>Termination</th>
                <th>Reference</th>
                <th>Replacement</th>
                <th>Cold-start forecast</th>
                <th>Remaining stock</th>
                <th>Clearance risk</th>
              </tr>
            </thead>
            <tbody>
              {lifecycleRows.map((row) => (
                <tr key={row.sku}>
                  <td>{row.sku}</td>
                  <td>{row.status}</td>
                  <td>{row.launch}</td>
                  <td>{row.termination}</td>
                  <td>{row.reference}</td>
                  <td>{row.replacement}</td>
                  <td>{row.forecast}</td>
                  <td>{row.stock}</td>
                  <td>{row.risk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">Phase-in Form</span>
            <h3>Select reference product</h3>
            <p>
              Category Manager chooses a reference SKU, validates launch date and approves
              cold-start forecast before the new SKU enters active matrix.
            </p>
            <div className="action-row">
              <button type="button">Select reference</button>
              <button type="button">Approve phase-in</button>
            </div>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Clearance Risk</span>
            <h3>Order blocked after termination</h3>
            <p>
              Remaining stock 420 creates high clearance risk. The phase-out process confirms
              replacement link, markdown and order block after termination date.
            </p>
            <div className="action-row">
              <button type="button">Approve markdown</button>
              <button type="button">Confirm order block</button>
            </div>
          </aside>
        </div>
      </section>

      <section className="data-section" aria-label="Supply Chain Dashboard">
        <div className="section-heading">
          <h2>Supply Chain Dashboard</h2>
          <p>Multi-echelon demand, DC stock, shortage and allocation preview</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>DC Demand Projection</span>
            <strong>DC001 / SKU001 demand 270</strong>
            <p>Store-level demand is aggregated into DC demand before supplier and WMS checks.</p>
          </article>
          <article className="feature-summary">
            <span>Shortage Event</span>
            <strong>Available 210, shortage 60</strong>
            <p>OPEN FNR Process Engine opens shortage review before the store order cutoff.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="DC demand allocation graph">
          <div className="chart-bars">
            <span style={{ height: "82%" }} title="Store demand" />
            <span style={{ height: "64%" }} title="DC available" />
            <span style={{ height: "22%" }} title="Shortage" />
            <span style={{ height: "78%" }} title="Allocated" />
          </div>
          <p>DC demand projection compares lower-level demand, WMS stock, shortage and allocation.</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Plan</th>
                <th>DC</th>
                <th>Region</th>
                <th>SKU</th>
                <th>Status</th>
                <th>Demand</th>
                <th>Available</th>
                <th>Shortage</th>
                <th>Cutoff</th>
                <th>Rule</th>
              </tr>
            </thead>
            <tbody>
              {dcPlanRows.map((row) => (
                <tr key={row.plan}>
                  <td>{row.plan}</td>
                  <td>{row.dc}</td>
                  <td>{row.region}</td>
                  <td>{row.sku}</td>
                  <td>{row.status}</td>
                  <td>{row.demand}</td>
                  <td>{row.available}</td>
                  <td>{row.shortage}</td>
                  <td>{row.cutoff}</td>
                  <td>{row.rule}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Store</th>
                <th>Priority</th>
                <th>Service risk</th>
                <th>Requested</th>
                <th>Allocated</th>
                <th>Unfilled</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {dcAllocationRows.map((row) => (
                <tr key={row.store}>
                  <td>{row.store}</td>
                  <td>{row.priority}</td>
                  <td>{row.serviceRisk}</td>
                  <td>{row.requested}</td>
                  <td>{row.allocated}</td>
                  <td>{row.unfilled}</td>
                  <td>{row.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">BPMN Task</span>
            <h3>Review DC shortage allocation</h3>
            <p>
              Supply Chain Manager checks WMS stock, demand aggregation and allocation priority
              before approving replenishment for stores served by DC001.
            </p>
            <div className="action-row">
              <button type="button">Open shortage</button>
              <button type="button">Approve allocation</button>
              <button type="button">Notify stores</button>
            </div>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Drill-down</span>
            <h3>DC -&gt; stores</h3>
            <p>
              Drill-down explains why S001 and S002 are covered first, while S003 remains unfilled
              due to the shortage after higher priority allocation.
            </p>
          </aside>
        </div>
      </section>

      <section className="data-section" aria-label="Performance report">
        <div className="section-heading">
          <h2>Performance Gate 1</h2>
          <p>Pilot-scale synthetic load, runtime baseline, bottlenecks and gate decision</p>
        </div>
        <div className="feature-grid">
          <article className="feature-summary">
            <span>Pilot Profile</span>
            <strong>3 000 stores x 5 500 SKU x 30 days</strong>
            <p>495M synthetic forecast rows are distributed across 8 shards for the first capacity gate.</p>
          </article>
          <article className="feature-summary">
            <span>Gate Decision</span>
            <strong>Passed</strong>
            <p>Batch runtime, API latency, UI latency, ClickHouse reads and Airflow runtime are below thresholds.</p>
          </article>
        </div>
        <div className="chart-panel" aria-label="Performance metric chart">
          <div className="chart-bars">
            <span style={{ height: "63%" }} title="Batch runtime" />
            <span style={{ height: "36%" }} title="API latency" />
            <span style={{ height: "70%" }} title="UI LCP" />
            <span style={{ height: "64%" }} title="ClickHouse read" />
            <span style={{ height: "70%" }} title="Airflow DAG" />
          </div>
          <p>Each bar shows actual value as a share of the configured Sprint 21 threshold.</p>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Metric</th>
                <th>Actual</th>
                <th>Threshold</th>
                <th>Unit</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {performanceMetrics.map((row) => (
                <tr key={row.metric}>
                  <td>{row.metric}</td>
                  <td>{row.value}</td>
                  <td>{row.threshold}</td>
                  <td>{row.unit}</td>
                  <td>{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Component</th>
                <th>Severity</th>
                <th>Finding</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {performanceBottlenecks.map((row) => (
                <tr key={row.component}>
                  <td>{row.component}</td>
                  <td>{row.severity}</td>
                  <td>{row.finding}</td>
                  <td>{row.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="dq-layout">
          <aside className="dq-detail">
            <span className="eyebrow">BPMN Gate</span>
            <h3>Evaluate performance gate</h3>
            <p>
              Performance Engineer runs synthetic load, batch benchmark, API latency benchmark and
              UI baseline before the DMN decision publishes gate result.
            </p>
            <div className="action-row">
              <button type="button">Open run</button>
              <button type="button">Publish report</button>
              <button type="button">Open regression</button>
            </div>
          </aside>
          <aside className="dq-detail">
            <span className="eyebrow">Waiver Case</span>
            <h3>Architect approval required</h3>
            <p>
              Failed blocking metrics open a regression case. Non-blocking latency regression can
              be waived only by Architect with audit trail and bottleneck owner.
            </p>
          </aside>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
