-- ============================================================================
-- Add item_type_id to task_types table
-- ============================================================================
-- This migration:
-- 1. Adds item_type_id column to task_types table
-- 2. Updates existing task types with their appropriate item_type_id values
-- 3. Soft-deletes task types that don't apply to any item type
-- 4. Adds NOT NULL constraint and foreign key
-- 5. Creates indexes for performance
-- ============================================================================

-- Step 1: Add item_type_id column (nullable initially for data migration)
ALTER TABLE task_types ADD COLUMN item_type_id INTEGER;

COMMENT ON COLUMN task_types.item_type_id IS 'Type of item this task applies to - foreign key to item_types table';

-- Step 2: Update existing task types with appropriate item_type_id values
-- Automobile tasks (item_type_id = 1)
UPDATE task_types SET item_type_id = 1 WHERE name = 'Oil Change';
UPDATE task_types SET item_type_id = 1 WHERE name = 'Air Filter Replacement';
UPDATE task_types SET item_type_id = 1 WHERE name = 'Brake Inspection';
UPDATE task_types SET item_type_id = 1 WHERE name = 'Spark Plug Replacement';

-- House tasks (item_type_id = 2)
UPDATE task_types SET item_type_id = 2 WHERE name = 'Roof Inspection';
UPDATE task_types SET item_type_id = 2 WHERE name = 'Gutter Cleaning';

-- Step 3: Soft-delete task types without an item type mapping
UPDATE task_types SET is_deleted = TRUE WHERE item_type_id IS NULL;

-- Step 4: Add NOT NULL constraint
ALTER TABLE task_types ALTER COLUMN item_type_id SET NOT NULL;

-- Step 5: Add foreign key constraint
ALTER TABLE task_types ADD CONSTRAINT fk_task_types_item_type_id
  FOREIGN KEY (item_type_id) REFERENCES item_types(id) ON DELETE RESTRICT;

-- Step 6: Create indexes for performance
CREATE INDEX idx_task_types_item_type_id ON task_types(item_type_id);
CREATE INDEX idx_task_types_item_type_is_deleted ON task_types(item_type_id, is_deleted);

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Summary of changes:
--   - Added item_type_id column to task_types
--   - Mapped 6 task types to appropriate item types
--   - Soft-deleted 1 unmapped task type (Blade Sharpening)
--   - Added foreign key and indexes
-- ============================================================================
