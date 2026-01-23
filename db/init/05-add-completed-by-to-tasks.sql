-- ============================================================================
-- Migration: Add completed_by field to tasks table
-- ============================================================================
-- Purpose: Record who performed the maintenance task
-- Examples:
--   - Person name: "John Smith", "Jane Doe"
--   - Business name: "Joe's Quick Lube", "ABC Roofing", "Smith Auto Center"
--   - Self-service: "Self"
-- ============================================================================

-- Add VARCHAR column for person/business who completed the task
ALTER TABLE tasks ADD COLUMN completed_by VARCHAR(255);

COMMENT ON COLUMN tasks.completed_by IS 'Person or business name who performed the maintenance task. Examples: "Self", "John Smith", "Joe''s Quick Lube", "ABC Roofing". Can be NULL if not recorded.';

-- ============================================================================
-- Populate completed_by for existing seed data
-- ============================================================================

-- Automobile tasks (item_id = 1)
-- Task 1: Oil change at 11 months ago
UPDATE tasks SET completed_by = 'Joe''s Quick Lube'
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '11 months';

-- Task 2: Oil change at 8 months ago with tire rotation
UPDATE tasks SET completed_by = 'Smith Auto Center'
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '8 months';

-- Task 3: Air filter replacement
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 1 AND task_type_id = 2 AND completed_at = CURRENT_DATE - INTERVAL '6 months';

-- Task 4: Brake inspection
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 1 AND task_type_id = 3 AND completed_at = CURRENT_DATE - INTERVAL '6 months';

-- Task 5: Oil change at 5 months ago
UPDATE tasks SET completed_by = 'Joe''s Quick Lube'
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '5 months';

-- Task 6: Oil change at 2 months ago
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '2 months';

-- Task 7: Brake pad replacement
UPDATE tasks SET completed_by = 'Smith Auto Center'
WHERE item_id = 1 AND task_type_id = 3 AND completed_at = CURRENT_DATE - INTERVAL '1 month';

-- House tasks (item_id = 2)
-- Task 8: Roof inspection
UPDATE tasks SET completed_by = 'ABC Roofing'
WHERE item_id = 2 AND task_type_id = 4 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task 9: Fall gutter cleaning
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 2 AND task_type_id = 5 AND completed_at = CURRENT_DATE - INTERVAL '9 months';

-- Task 10: Spring gutter cleaning
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 2 AND task_type_id = 5 AND completed_at = CURRENT_DATE - INTERVAL '3 months';

-- Snowblower tasks (item_id = 3)
-- Task 11: Pre-season oil change
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 3 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task 12: Spark plug replacement
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 3 AND task_type_id = 6 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task 13: Blade sharpening
UPDATE tasks SET completed_by = 'Winter Equipment Service'
WHERE item_id = 3 AND task_type_id = 7 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task 14: Mid-season oil change
UPDATE tasks SET completed_by = 'Self'
WHERE item_id = 3 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '4 months';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
