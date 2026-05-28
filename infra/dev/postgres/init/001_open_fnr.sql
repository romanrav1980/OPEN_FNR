CREATE SCHEMA IF NOT EXISTS open_fnr;

CREATE TABLE IF NOT EXISTS open_fnr.dev_healthcheck
(
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO open_fnr.dev_healthcheck (service_name)
VALUES ('postgres')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS open_fnr.ingestion_batches
(
    batch_id text PRIMARY KEY,
    domain text NOT NULL,
    business_date date NOT NULL,
    source_system text NOT NULL,
    status text NOT NULL,
    row_count bigint NOT NULL CHECK (row_count >= 0),
    checksum text NOT NULL,
    severity text NOT NULL DEFAULT 'info',
    message text,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ingestion_batches_business_date
    ON open_fnr.ingestion_batches (business_date, domain, status);

CREATE TABLE IF NOT EXISTS open_fnr.dq_rules
(
    rule_id text PRIMARY KEY,
    domain text NOT NULL,
    dimension text NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    severity text NOT NULL,
    blocking boolean NOT NULL,
    owner_role text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS open_fnr.dq_incidents
(
    incident_id text PRIMARY KEY,
    rule_id text NOT NULL REFERENCES open_fnr.dq_rules(rule_id),
    batch_id text NOT NULL,
    domain text NOT NULL,
    business_date date NOT NULL,
    severity text NOT NULL,
    status text NOT NULL,
    blocking boolean NOT NULL,
    affected_rows bigint NOT NULL CHECK (affected_rows >= 0),
    affected_scope text NOT NULL,
    message text NOT NULL,
    owner_role text NOT NULL,
    waiver_reason text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_dq_incidents_business_date
    ON open_fnr.dq_incidents (business_date, domain, severity, status);

CREATE TABLE IF NOT EXISTS open_fnr.feature_mart_versions
(
    feature_version text PRIMARY KEY,
    business_date date NOT NULL,
    status text NOT NULL,
    input_batch_ids jsonb NOT NULL,
    active_pairs bigint NOT NULL CHECK (active_pairs >= 0),
    feature_count integer NOT NULL CHECK (feature_count >= 0),
    quality_status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz
);

CREATE INDEX IF NOT EXISTS ix_feature_mart_versions_business_date
    ON open_fnr.feature_mart_versions (business_date, status);
