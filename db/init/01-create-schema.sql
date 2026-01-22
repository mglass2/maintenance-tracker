-- ============================================================================
-- Maintenance Tracker Database Schema
-- ============================================================================
-- This schema implements a soft-delete pattern for all tables.
--
-- CRITICAL: All queries in the application MUST filter by is_deleted = FALSE
-- to exclude deleted records. Hard deletes are prevented via RESTRICT
-- constraints - use UPDATE to set is_deleted = TRUE instead.
-- ============================================================================

-- ============================================================================
-- TABLE: users
-- ============================================================================
-- Stores user account information. Users own items and track maintenance.
--
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'User accounts for the maintenance tracking application';
COMMENT ON COLUMN users.is_deleted IS 'Soft delete flag - TRUE means deleted, FALSE means active';

-- ============================================================================
-- TABLE: item_types
-- ============================================================================
-- Defines categories of items (e.g., "automobile", "house", "snowblower").
--
CREATE TABLE item_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE item_types IS 'Categories of items that can be maintained';
COMMENT ON COLUMN item_types.name IS 'Unique name for the item type (e.g., automobile, house)';
COMMENT ON COLUMN item_types.is_deleted IS 'Soft delete flag - TRUE means deleted, FALSE means active';

-- ============================================================================
-- TABLE: items
-- ============================================================================
-- Stores individual items owned by users (or orphaned items with no owner).
--
-- IMPORTANT: user_id is NULLABLE - items can exist without an owner.
-- Foreign keys use ON DELETE RESTRICT to prevent hard deletes.
--
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
  item_type_id INTEGER NOT NULL REFERENCES item_types(id) ON DELETE RESTRICT,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  acquired_at DATE,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE items IS 'Individual items that require maintenance tracking';
COMMENT ON COLUMN items.user_id IS 'Owner of the item (NULLABLE - items can be orphaned)';
COMMENT ON COLUMN items.item_type_id IS 'Type/category of this item';
COMMENT ON COLUMN items.acquired_at IS 'Date when the user acquired this item';
COMMENT ON COLUMN items.is_deleted IS 'Soft delete flag - TRUE means deleted, FALSE means active';

-- ============================================================================
-- TABLE: task_types
-- ============================================================================
-- Defines categories of maintenance tasks (e.g., "Oil Change", "Roof Inspection").
--
-- NOTE: Maintenance intervals will be defined later in a separate table.
-- Different items may have different intervals for the same task type.
--
CREATE TABLE task_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE task_types IS 'Categories of maintenance tasks that can be performed';
COMMENT ON COLUMN task_types.name IS 'Unique name for the task type (e.g., Oil Change)';
COMMENT ON COLUMN task_types.is_deleted IS 'Soft delete flag - TRUE means deleted, FALSE means active';

-- ============================================================================
-- TABLE: tasks
-- ============================================================================
-- Records individual maintenance task instances performed on items.
-- This is the core historical data for maintenance tracking.
--
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
  task_type_id INTEGER NOT NULL REFERENCES task_types(id) ON DELETE RESTRICT,
  completed_at DATE NOT NULL,
  notes TEXT,
  cost DECIMAL(10, 2),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT cost_non_negative CHECK (cost IS NULL OR cost >= 0)
);

COMMENT ON TABLE tasks IS 'Individual maintenance task instances performed on items';
COMMENT ON COLUMN tasks.item_id IS 'The item this task was performed on';
COMMENT ON COLUMN tasks.task_type_id IS 'The type of maintenance task performed';
COMMENT ON COLUMN tasks.completed_at IS 'Date when the maintenance was completed';
COMMENT ON COLUMN tasks.cost IS 'Cost of the maintenance (must be non-negative)';
COMMENT ON COLUMN tasks.is_deleted IS 'Soft delete flag - TRUE means deleted, FALSE means active';
COMMENT ON CONSTRAINT cost_non_negative ON tasks IS 'Ensures cost is never negative';

-- ============================================================================
-- INDEXES
-- ============================================================================
-- Performance indexes on foreign keys, soft delete flags, and frequently
-- queried columns.
--

-- Foreign key indexes for efficient joins
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_item_type_id ON items(item_type_id);
CREATE INDEX idx_tasks_item_id ON tasks(item_id);
CREATE INDEX idx_tasks_task_type_id ON tasks(task_type_id);

-- Date index for querying task history and future forecasting
CREATE INDEX idx_tasks_completed_at ON tasks(completed_at);

-- Email index for user lookups (future authentication)
CREATE INDEX idx_users_email ON users(email);

-- Soft delete indexes (queries will filter WHERE is_deleted = FALSE)
CREATE INDEX idx_users_is_deleted ON users(is_deleted);
CREATE INDEX idx_item_types_is_deleted ON item_types(is_deleted);
CREATE INDEX idx_items_is_deleted ON items(is_deleted);
CREATE INDEX idx_task_types_is_deleted ON task_types(is_deleted);
CREATE INDEX idx_tasks_is_deleted ON tasks(is_deleted);

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================