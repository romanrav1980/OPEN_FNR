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
