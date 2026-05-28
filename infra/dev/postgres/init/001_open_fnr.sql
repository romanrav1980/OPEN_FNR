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
