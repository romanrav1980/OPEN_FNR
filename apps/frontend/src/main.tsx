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
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
