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
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
