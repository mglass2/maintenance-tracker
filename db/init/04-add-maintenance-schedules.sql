-- ============================================================================
-- Maintenance Tracker Maintenance Schedule Tables
-- ============================================================================
-- These tables implement the maintenance scheduling system to support:
-- 1. Maintenance templates that define default task schedules for item types
-- 2. Item maintenance plans that track actual schedules for specific items
--
-- This schema supports both time-based and custom-interval maintenance
-- (e.g., mileage-based, hours-based) using JSONB fields.
-- ============================================================================

-- ============================================================================
-- TABLE: maintenance_template
-- ============================================================================
-- Defines default maintenance schedules for each item type.
-- Acts as a template that gets instantiated when a new item is created.
--
-- Purpose: Define which task types are relevant for an item type,
-- with default maintenance intervals.
--
CREATE TABLE maintenance_template (
  id SERIAL PRIMARY KEY,
  item_type_id INTEGER NOT NULL REFERENCES item_types(id) ON DELETE RESTRICT,
  task_type_id INTEGER NOT NULL REFERENCES task_types(id) ON DELETE RESTRICT,
  time_interval_days INTEGER NOT NULL,
  custom_interval JSONB,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Ensure time_interval is positive
  CONSTRAINT maintenance_template_time_interval_positive CHECK (time_interval_days > 0)
);

-- Partial unique index: ensure each task type appears only once per item type (for active records)
CREATE UNIQUE INDEX idx_maintenance_template_unique_per_item_type
  ON maintenance_template(item_type_id, task_type_id) WHERE is_deleted = FALSE;

COMMENT ON TABLE maintenance_template IS
  'Defines default maintenance schedules for item types. Serves as a template when creating new items of that type.';

COMMENT ON COLUMN maintenance_template.item_type_id IS
  'The item type this maintenance template applies to';

COMMENT ON COLUMN maintenance_template.task_type_id IS
  'The task type in this maintenance schedule';

COMMENT ON COLUMN maintenance_template.time_interval_days IS
  'Default number of days between maintenance tasks (must be positive)';

COMMENT ON COLUMN maintenance_template.custom_interval IS
  'JSONB field for custom interval definitions (e.g., mileage, hours). Example: {"type": "mileage", "value": 5000, "unit": "miles"} or {"type": "hours", "value": 100, "unit": "hours"}. Null if only time-based intervals.';

COMMENT ON COLUMN maintenance_template.is_deleted IS
  'Soft delete flag - TRUE means deleted, FALSE means active';

COMMENT ON INDEX idx_maintenance_template_unique_per_item_type IS
  'Partial unique index: ensures each task type appears only once per item type (for active records only)';

COMMENT ON CONSTRAINT maintenance_template_time_interval_positive ON maintenance_template IS
  'Ensures time interval is always positive';


-- ============================================================================
-- TABLE: item_maintenance_plan
-- ============================================================================
-- Tracks the actual maintenance intervals for a specific item.
-- Allows each item to have custom intervals (overriding the template defaults).
--
-- Purpose: Enable forecasting of future maintenance for a given item.
-- The user can accept template defaults or customize intervals per item.
--
CREATE TABLE item_maintenance_plan (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
  task_type_id INTEGER NOT NULL REFERENCES task_types(id) ON DELETE RESTRICT,
  time_interval_days INTEGER NOT NULL,
  custom_interval JSONB,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Ensure time_interval is positive
  CONSTRAINT item_maintenance_plan_time_interval_positive CHECK (time_interval_days > 0)
);

-- Partial unique index: ensure each task type appears only once per item (for active records)
CREATE UNIQUE INDEX idx_item_maintenance_plan_unique_per_item
  ON item_maintenance_plan(item_id, task_type_id) WHERE is_deleted = FALSE;

COMMENT ON TABLE item_maintenance_plan IS
  'Tracks the actual maintenance intervals for a specific item. Allows customization of intervals per item (overriding template defaults). Used for forecasting future maintenance.';

COMMENT ON COLUMN item_maintenance_plan.item_id IS
  'The item this maintenance plan applies to';

COMMENT ON COLUMN item_maintenance_plan.task_type_id IS
  'The task type in this maintenance plan';

COMMENT ON COLUMN item_maintenance_plan.time_interval_days IS
  'Number of days between maintenance tasks for this item (must be positive)';

COMMENT ON COLUMN item_maintenance_plan.custom_interval IS
  'JSONB field for custom interval definitions specific to this item. Example: {"type": "mileage", "value": 3000, "unit": "miles"} for oil changes. If the maintenance_template defines a custom_interval, this field MUST be set.';

COMMENT ON COLUMN item_maintenance_plan.is_deleted IS
  'Soft delete flag - TRUE means deleted, FALSE means active';

COMMENT ON INDEX idx_item_maintenance_plan_unique_per_item IS
  'Partial unique index: ensures each task type appears only once per item (for active records only)';

COMMENT ON CONSTRAINT item_maintenance_plan_time_interval_positive ON item_maintenance_plan IS
  'Ensures time interval is always positive';


-- ============================================================================
-- INDEXES
-- ============================================================================
-- Performance indexes on foreign keys, soft delete flags, and frequently
-- queried columns for maintenance scheduling queries.
--

-- Foreign key indexes for efficient joins on maintenance_template
CREATE INDEX idx_maintenance_template_item_type_id
  ON maintenance_template(item_type_id);
CREATE INDEX idx_maintenance_template_task_type_id
  ON maintenance_template(task_type_id);

-- Foreign key indexes for efficient joins on item_maintenance_plan
CREATE INDEX idx_item_maintenance_plan_item_id
  ON item_maintenance_plan(item_id);
CREATE INDEX idx_item_maintenance_plan_task_type_id
  ON item_maintenance_plan(task_type_id);

-- Soft delete indexes
CREATE INDEX idx_maintenance_template_is_deleted
  ON maintenance_template(is_deleted);
CREATE INDEX idx_item_maintenance_plan_is_deleted
  ON item_maintenance_plan(is_deleted);

-- Composite index for common query pattern:
-- "Get all task types for a given item that need to be scheduled"
CREATE INDEX idx_item_maintenance_plan_item_id_is_deleted
  ON item_maintenance_plan(item_id, is_deleted);

-- Composite index for common query pattern:
-- "Get all task types for a given item type template"
CREATE INDEX idx_maintenance_template_item_type_task_type
  ON maintenance_template(item_type_id, task_type_id) WHERE is_deleted = FALSE;

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================
