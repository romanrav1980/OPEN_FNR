CREATE SCHEMA IF NOT EXISTS open_fnr;

CREATE TABLE IF NOT EXISTS open_fnr.dev_healthcheck
(
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS open_fnr.schema_migrations
(
    version text PRIMARY KEY,
    description text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO open_fnr.schema_migrations (version, description)
VALUES ('001', 'initial open_fnr schema')
ON CONFLICT (version) DO NOTHING;

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

CREATE TABLE IF NOT EXISTS open_fnr.forecast_versions
(
    forecast_version text PRIMARY KEY,
    run_date date NOT NULL,
    horizon_days integer NOT NULL CHECK (horizon_days > 0),
    status text NOT NULL,
    model_version text NOT NULL,
    data_version text NOT NULL,
    feature_version text NOT NULL,
    rows bigint NOT NULL CHECK (rows >= 0),
    wape numeric(12, 6) NOT NULL CHECK (wape >= 0),
    bias numeric(12, 6) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz
);

CREATE INDEX IF NOT EXISTS ix_forecast_versions_run_date
    ON open_fnr.forecast_versions (run_date, status);

CREATE TABLE IF NOT EXISTS open_fnr.audit_events
(
    event_id text PRIMARY KEY,
    event_type text NOT NULL,
    actor text NOT NULL,
    actor_role text,
    object_type text NOT NULL,
    object_id text NOT NULL,
    action text NOT NULL,
    reason text NOT NULL,
    correlation_id text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_events_object
    ON open_fnr.audit_events (object_type, object_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_audit_events_actor
    ON open_fnr.audit_events (actor, created_at DESC);

CREATE TABLE IF NOT EXISTS open_fnr.integration_batches
(
    batch_id text PRIMARY KEY,
    source_system text NOT NULL,
    contract_name text NOT NULL,
    contract_version text NOT NULL,
    business_date date NOT NULL,
    status text NOT NULL,
    row_count bigint NOT NULL CHECK (row_count >= 0),
    checksum text NOT NULL,
    idempotency_key text NOT NULL UNIQUE,
    reject_count bigint NOT NULL DEFAULT 0 CHECK (reject_count >= 0),
    correlation_id text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_integration_batches_source_date
    ON open_fnr.integration_batches (source_system, business_date, status);

CREATE TABLE IF NOT EXISTS open_fnr.process_tasks
(
    task_id text PRIMARY KEY,
    process_instance_id text NOT NULL,
    process_key text NOT NULL,
    name text NOT NULL,
    status text NOT NULL,
    assigned_role text NOT NULL,
    candidate_roles jsonb NOT NULL DEFAULT '[]'::jsonb,
    available_actions jsonb NOT NULL DEFAULT '[]'::jsonb,
    sla_due_at timestamptz NOT NULL,
    business_key text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz
);

CREATE INDEX IF NOT EXISTS ix_process_tasks_process_status
    ON open_fnr.process_tasks (process_key, status, sla_due_at);

CREATE INDEX IF NOT EXISTS ix_process_tasks_business_key
    ON open_fnr.process_tasks (business_key, process_key);

CREATE TABLE IF NOT EXISTS open_fnr.process_task_events
(
    event_id text PRIMARY KEY,
    process_instance_id text NOT NULL,
    task_id text REFERENCES open_fnr.process_tasks(task_id),
    event_type text NOT NULL,
    actor text NOT NULL,
    actor_role text,
    message text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_process_task_events_instance
    ON open_fnr.process_task_events (process_instance_id, created_at);

CREATE TABLE IF NOT EXISTS open_fnr.operational_decisions
(
    decision_id text PRIMARY KEY,
    decision_type text NOT NULL,
    object_type text NOT NULL,
    object_id text NOT NULL,
    status text NOT NULL,
    actor text NOT NULL,
    actor_role text,
    idempotency_key text NOT NULL UNIQUE,
    correlation_id text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_operational_decisions_object
    ON open_fnr.operational_decisions (object_type, object_id, status);

CREATE TABLE IF NOT EXISTS open_fnr.publication_packages
(
    package_id text PRIMARY KEY,
    package_type text NOT NULL,
    target_system text NOT NULL,
    status text NOT NULL,
    idempotency_key text NOT NULL UNIQUE,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_publication_packages_target_status
    ON open_fnr.publication_packages (target_system, status);

CREATE TABLE IF NOT EXISTS open_fnr.export_attempts
(
    attempt_id text PRIMARY KEY,
    package_id text NOT NULL REFERENCES open_fnr.publication_packages(package_id),
    target_system text NOT NULL,
    status text NOT NULL,
    retry_count integer NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    idempotency_key text NOT NULL,
    response_status integer,
    response_message text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_export_attempts_package
    ON open_fnr.export_attempts (package_id, created_at DESC);
