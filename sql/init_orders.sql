CREATE TABLE IF NOT EXISTS customer_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    product_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customer_orders (customer_id, order_date, total_amount, product_name)
VALUES
    (101, CURRENT_DATE - INTERVAL '2 day', 120.50, 'mobile_scanner'),
    (102, CURRENT_DATE - INTERVAL '1 day', 80.00, 'data_terminal'),
    (103, CURRENT_DATE, 240.00, 'warehouse_license'),
    (104, CURRENT_DATE, 60.75, 'support_package');

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dqops') THEN
        CREATE ROLE dqops LOGIN PASSWORD 'dqops';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE dz8 TO dqops;
GRANT USAGE ON SCHEMA public TO dqops;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dqops;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dqops;
