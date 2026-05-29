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

CREATE TABLE IF NOT EXISTS open_fnr.raw_pos_sales_lines
(
    batch_id String,
    receipt_id String,
    line_id String,
    business_date Date,
    store_id String,
    sku_id String,
    sales_qty Float64,
    gross_amount Float64,
    net_amount Float64,
    discount_amount Float64,
    currency String,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, receipt_id, line_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_dwh_sales_history
(
    batch_id String,
    history_id String,
    business_date Date,
    store_id String,
    sku_id String,
    sales_qty Float64,
    gross_amount Float64,
    net_amount Float64,
    discount_amount Float64,
    receipt_count UInt32,
    return_qty Float64,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, history_id);

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

CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_stock_snapshots
(
    batch_id String,
    snapshot_id String,
    snapshot_at DateTime,
    business_date Date,
    location_id String,
    location_type String,
    sku_id String,
    on_hand_qty Float64,
    reserved_qty Float64,
    available_qty Float64,
    damaged_qty Float64,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, location_id, sku_id, snapshot_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_open_orders
(
    batch_id String,
    order_id String,
    line_id String,
    order_date Date,
    expected_delivery_date Date,
    source_location_id String,
    target_location_id String,
    sku_id String,
    ordered_qty Float64,
    confirmed_qty Float64,
    status String,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(expected_delivery_date)
ORDER BY (expected_delivery_date, target_location_id, sku_id, order_id, line_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_in_transit
(
    batch_id String,
    shipment_id String,
    line_id String,
    ship_date Date,
    eta_date Date,
    source_location_id String,
    target_location_id String,
    sku_id String,
    shipped_qty Float64,
    received_qty Float64,
    status String,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(eta_date)
ORDER BY (eta_date, target_location_id, sku_id, shipment_id, line_id);

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

CREATE TABLE IF NOT EXISTS open_fnr.raw_erp_prices
(
    batch_id String,
    price_id String,
    sku_id String,
    location_scope String,
    valid_from Date,
    valid_to Nullable(Date),
    regular_price Float64,
    selling_price Float64,
    currency String,
    vat_rate Float64,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(valid_from)
ORDER BY (valid_from, location_scope, sku_id, price_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_erp_order_export_statuses
(
    batch_id String,
    export_id String,
    proposal_id String,
    external_order_id Nullable(String),
    exported_at DateTime,
    target_system String,
    status String,
    retry_count UInt32,
    error_code Nullable(String),
    error_message Nullable(String),
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(exported_at)
ORDER BY (exported_at, target_system, status, proposal_id, export_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_erp_supplier_terms
(
    batch_id String,
    supplier_term_id String,
    supplier_id String,
    sku_id String,
    location_scope String,
    valid_from Date,
    valid_to Nullable(Date),
    lead_time_days UInt32,
    moq_qty Float64,
    pack_size_qty Float64,
    order_calendar_id Nullable(String),
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(valid_from)
ORDER BY (valid_from, supplier_id, sku_id, location_scope, supplier_term_id);

CREATE TABLE IF NOT EXISTS open_fnr.dq_error_rows
(
    incident_id String,
    rule_id String,
    batch_id String,
    business_date Date,
    domain String,
    store_id String,
    sku_id String,
    error_payload String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, domain, incident_id, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_mdm_products
(
    batch_id String,
    sku_id String,
    product_name String,
    category_id String,
    category_path String,
    brand_id Nullable(String),
    supplier_id Nullable(String),
    uom String,
    shelf_life_days Nullable(UInt32),
    lifecycle_status String,
    replacement_sku_id Nullable(String),
    is_fresh UInt8,
    is_active UInt8,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY tuple()
ORDER BY (category_id, sku_id, batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_mdm_stores
(
    batch_id String,
    store_id String,
    store_name String,
    region_id String,
    format_id String,
    timezone String,
    opening_date Nullable(Date),
    closing_date Nullable(Date),
    replenishment_calendar_id Nullable(String),
    warehouse_id Nullable(String),
    is_active UInt8,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY tuple()
ORDER BY (region_id, format_id, store_id, batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.raw_promo_plans
(
    batch_id String,
    promo_id String,
    promo_name String,
    sku_id String,
    store_scope_id String,
    date_from Date,
    date_to Date,
    regular_price Float64,
    promo_price Float64,
    discount_pct Float64,
    display_type Nullable(String),
    display_location Nullable(String),
    display_capacity_units Nullable(Float64),
    mechanics Nullable(String),
    forecast_lock UInt8,
    source_system String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(date_from)
ORDER BY (date_from, date_to, store_scope_id, sku_id, promo_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_sales_daily
(
    business_date Date,
    store_id String,
    sku_id String,
    sales_qty Float64,
    gross_amount Float64,
    net_amount Float64,
    discount_amount Float64,
    receipt_count UInt32,
    return_qty Float64,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, store_id, sku_id, source_batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_stock_snapshot_daily
(
    business_date Date,
    location_id String,
    location_type String,
    sku_id String,
    on_hand_qty Float64,
    reserved_qty Float64,
    available_qty Float64,
    damaged_qty Float64,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, location_id, sku_id, source_batch_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_open_orders
(
    order_id String,
    line_id String,
    order_date Date,
    expected_delivery_date Date,
    source_location_id String,
    target_location_id String,
    sku_id String,
    ordered_qty Float64,
    confirmed_qty Float64,
    status String,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(expected_delivery_date)
ORDER BY (expected_delivery_date, target_location_id, sku_id, order_id, line_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_in_transit
(
    shipment_id String,
    line_id String,
    ship_date Date,
    eta_date Date,
    source_location_id String,
    target_location_id String,
    sku_id String,
    shipped_qty Float64,
    received_qty Float64,
    status String,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(eta_date)
ORDER BY (eta_date, target_location_id, sku_id, shipment_id, line_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_prices
(
    sku_id String,
    location_scope String,
    valid_from Date,
    valid_to Nullable(Date),
    regular_price Float64,
    selling_price Float64,
    currency String,
    vat_rate Float64,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(valid_from)
ORDER BY (valid_from, location_scope, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.clean_promo_plans
(
    promo_id String,
    sku_id String,
    store_scope_id String,
    date_from Date,
    date_to Date,
    regular_price Float64,
    promo_price Float64,
    discount_pct Float64,
    display_type Nullable(String),
    display_location Nullable(String),
    display_capacity_units Nullable(Float64),
    mechanics Nullable(String),
    forecast_lock UInt8,
    source_batch_id String,
    quality_status String,
    published_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(date_from)
ORDER BY (date_from, date_to, store_scope_id, sku_id, promo_id);

CREATE TABLE IF NOT EXISTS open_fnr.active_matrix_daily
(
    business_date Date,
    store_id String,
    sku_id String,
    region_id String,
    category_id String,
    assortment_valid UInt8,
    store_active UInt8,
    sku_active UInt8,
    include_pair UInt8,
    feature_version String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (business_date, region_id, category_id, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.feature_store_daily
(
    feature_version String,
    business_date Date,
    store_id String,
    sku_id String,
    sales_lag_7d Float64,
    sales_rolling_mean_28d Float64,
    current_selling_price Float64,
    stock_available_flag UInt8,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(business_date)
ORDER BY (feature_version, business_date, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.stock_projection_daily
(
    projection_version String,
    run_date Date,
    projection_date Date,
    store_id String,
    sku_id String,
    opening_stock_qty Float64,
    demand_projection_qty Float64,
    open_order_receipt_qty Float64,
    in_transit_receipt_qty Float64,
    projected_stock_qty Float64,
    safety_stock_qty Float64,
    stock_out_risk String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(run_date)
ORDER BY (run_date, projection_date, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.kpi_daily
(
    calculation_version String,
    period_start Date,
    period_end Date,
    network String,
    region_id String,
    category_id String,
    store_id String,
    sku_id String,
    actual_qty Float64,
    ml_forecast_qty Float64,
    final_forecast_qty Float64,
    wape Float64,
    bias Float64,
    service_level Float64,
    out_of_stock_rate Float64,
    overstock_value Float64,
    lost_sales_value Float64,
    waste_value Float64,
    proposal_acceptance_rate Float64,
    calculated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(period_end)
ORDER BY (period_end, region_id, category_id, store_id, sku_id);

CREATE TABLE IF NOT EXISTS open_fnr.diagnostic_insights
(
    insight_id String,
    run_date Date,
    object_type String,
    object_id String,
    root_cause String,
    confidence Float64,
    severity String,
    recommended_action String,
    evidence_count UInt32,
    status String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(run_date)
ORDER BY (run_date, severity, object_type, object_id, insight_id);

CREATE TABLE IF NOT EXISTS open_fnr.supplier_performance_daily
(
    calculation_date Date,
    supplier_id String,
    fill_rate Float64,
    on_time_rate Float64,
    confirmation_rate Float64,
    open_exceptions UInt32,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(calculation_date)
ORDER BY (calculation_date, supplier_id);
