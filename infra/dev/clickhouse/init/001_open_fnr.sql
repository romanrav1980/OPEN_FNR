CREATE DATABASE IF NOT EXISTS open_fnr;

CREATE TABLE IF NOT EXISTS open_fnr.forecast_daily
(
    forecast_version String,
    run_date Date,
    forecast_date Date,
    store_id String,
    sku_id String,
    regular_forecast_qty Float64,
    promo_uplift_forecast_qty Float64,
    total_forecast_qty Float64,
    model_version String,
    data_version String,
    quality_flag String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(run_date)
ORDER BY (run_date, forecast_date, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.order_proposals
(
    proposal_version String,
    run_date Date,
    order_date Date,
    expected_delivery_date Date,
    source_location_id String,
    target_location_id String,
    sku_id String,
    forecast_demand_qty Float64,
    projected_stock_qty Float64,
    safety_stock_qty Float64,
    presentation_stock_qty Float64,
    net_requirement_qty Float64,
    order_proposal_qty Float64,
    status String,
    explanation String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(run_date)
ORDER BY (run_date, order_date, target_location_id, sku_id);
