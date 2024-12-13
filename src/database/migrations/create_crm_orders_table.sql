-- Создаем таблицу для хранения заказов из CRM
CREATE TABLE IF NOT EXISTS crm_orders (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE,
    order_sum DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    is_cancelled BOOLEAN DEFAULT FALSE,
    currency VARCHAR(3) NOT NULL,
    delivery_cost DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем индекс для быстрого поиска по order_id
CREATE INDEX IF NOT EXISTS idx_crm_orders_order_id ON crm_orders(order_id);

-- Создаем функцию для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_crm_orders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создаем триггер для автоматического обновления updated_at
DROP TRIGGER IF EXISTS update_crm_orders_updated_at ON crm_orders;
CREATE TRIGGER update_crm_orders_updated_at
    BEFORE UPDATE ON crm_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_crm_orders_updated_at();
