-- Maintenance Tracker Database Schema

-- Items table: Stores the items that need maintenance
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    purchase_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Tasks table: Stores types of maintenance tasks
CREATE TABLE IF NOT EXISTS maintenance_task_types (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    frequency_days INTEGER NOT NULL,
    estimated_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task History table: Records completed maintenance tasks
CREATE TABLE IF NOT EXISTS task_history (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    task_type_id INTEGER NOT NULL REFERENCES maintenance_task_types(id) ON DELETE CASCADE,
    completed_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forecasted Schedule table: Stores predicted future maintenance schedules
CREATE TABLE IF NOT EXISTS forecasted_schedule (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    task_type_id INTEGER NOT NULL REFERENCES maintenance_task_types(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at);
CREATE INDEX IF NOT EXISTS idx_maintenance_task_types_item_id ON maintenance_task_types(item_id);
CREATE INDEX IF NOT EXISTS idx_task_history_item_id ON task_history(item_id);
CREATE INDEX IF NOT EXISTS idx_task_history_completed_date ON task_history(completed_date);
CREATE INDEX IF NOT EXISTS idx_forecasted_schedule_item_id ON forecasted_schedule(item_id);
CREATE INDEX IF NOT EXISTS idx_forecasted_schedule_scheduled_date ON forecasted_schedule(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_forecasted_schedule_is_completed ON forecasted_schedule(is_completed);
