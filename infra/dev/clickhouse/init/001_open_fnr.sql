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

CREATE TABLE IF NOT EXISTS open_fnr.staging_sales_daily
(
    batch_id String,
    business_date Date,
    store_id String,
    sku_id String,
    sales_qty Float64,
    sales_amount Float64,
    receipt_count UInt32,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.staging_stock_daily
(
    batch_id String,
    business_date Date,
    store_id String,
    sku_id String,
    on_hand_qty Float64,
    reserved_qty Float64,
    in_transit_qty Float64,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.staging_prices_daily
(
    batch_id String,
    business_date Date,
    store_id String,
    sku_id String,
    regular_price Float64,
    selling_price Float64,
    currency String,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, batch_id);
