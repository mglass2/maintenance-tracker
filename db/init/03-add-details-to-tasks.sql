-- ============================================================================
-- Migration: Add JSONB details field to tasks table
-- ============================================================================
-- Purpose: Store task-specific information that varies by item type
-- Examples:
--   - Automobile: {"mileage": 75000, "oil_type": "5W-30 Synthetic"}
--   - House: {"contractor": "ABC Roofing", "areas_inspected": ["shingles"]}
--   - Snowblower: {"hours_of_operation": 45, "oil_type": "10W-30"}
-- ============================================================================

-- Add JSONB column for flexible task details
ALTER TABLE tasks ADD COLUMN details JSONB;

COMMENT ON COLUMN tasks.details IS 'Task-specific information stored as JSONB. Structure varies by item type and task type. Examples: {"mileage": 75000, "oil_type": "5W-30"} for automobiles, {"contractor": "ABC Roofing"} for house tasks.';

-- Create GIN index for efficient JSONB queries (supports @>, ?, ?&, ?| operators)
CREATE INDEX idx_tasks_details ON tasks USING GIN (details);

COMMENT ON INDEX idx_tasks_details IS 'GIN index for JSONB containment and existence queries on task details';

-- ============================================================================
-- Populate details for existing seed data
-- ============================================================================

-- Automobile tasks (item_id = 1)
-- Task ID 1: Oil change at 11 months ago
UPDATE tasks SET details = '{"mileage": 75000, "oil_type": "5W-30 Synthetic Blend", "filter_brand": "Fram"}'::jsonb
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '11 months';

-- Task ID 2: Oil change at 8 months ago
UPDATE tasks SET details = '{"mileage": 84000, "oil_type": "5W-30 Synthetic Blend", "filter_brand": "Fram", "tire_rotation": true}'::jsonb
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '8 months';

-- Task ID 3: Air filter replacement
UPDATE tasks SET details = '{"filter_types": ["cabin", "engine"], "brands": ["Bosch", "Fram"]}'::jsonb
WHERE item_id = 1 AND task_type_id = 2 AND completed_at = CURRENT_DATE - INTERVAL '6 months';

-- Task ID 4: Brake inspection
UPDATE tasks SET details = '{"front_pads_thickness_mm": 6, "rear_pads_thickness_mm": 7, "rotor_condition": "good"}'::jsonb
WHERE item_id = 1 AND task_type_id = 3 AND completed_at = CURRENT_DATE - INTERVAL '6 months';

-- Task ID 5: Oil change at 5 months ago
UPDATE tasks SET details = '{"mileage": 92000, "oil_type": "5W-30 Synthetic Blend"}'::jsonb
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '5 months';

-- Task ID 6: Oil change at 2 months ago
UPDATE tasks SET details = '{"mileage": 101000, "oil_type": "5W-30 Synthetic Blend", "fluids_topped": ["coolant", "washer"]}'::jsonb
WHERE item_id = 1 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '2 months';

-- Task ID 7: Brake pad replacement
UPDATE tasks SET details = '{"mileage": 105000, "front_pads_thickness_mm": 2, "parts_replaced": ["front pads", "front rotors"], "warranty_months": 12}'::jsonb
WHERE item_id = 1 AND task_type_id = 3 AND completed_at = CURRENT_DATE - INTERVAL '1 month';

-- House tasks (item_id = 2)
-- Task ID 8: Roof inspection
UPDATE tasks SET details = '{"contractor": "ABC Roofing", "areas_inspected": ["shingles", "flashing", "chimney"], "issues_found": ["minor flashing repair"], "next_full_replacement_year": 2028}'::jsonb
WHERE item_id = 2 AND task_type_id = 4 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task ID 9: Fall gutter cleaning
UPDATE tasks SET details = '{"debris_removed_lbs": 15, "downspouts_checked": true, "minor_repairs": ["reattached section B"]}'::jsonb
WHERE item_id = 2 AND task_type_id = 5 AND completed_at = CURRENT_DATE - INTERVAL '9 months';

-- Task ID 10: Spring gutter cleaning
UPDATE tasks SET details = '{"debris_removed_lbs": 8, "downspouts_checked": true}'::jsonb
WHERE item_id = 2 AND task_type_id = 5 AND completed_at = CURRENT_DATE - INTERVAL '3 months';

-- Snowblower tasks (item_id = 3)
-- Task ID 11: Pre-season oil change
UPDATE tasks SET details = '{"hours_of_operation": 0, "oil_type": "10W-30", "prep_type": "pre-season"}'::jsonb
WHERE item_id = 3 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task ID 12: Spark plug replacement
UPDATE tasks SET details = '{"spark_plug_brand": "NGK", "gap_mm": 0.7, "old_plug_condition": "worn"}'::jsonb
WHERE item_id = 3 AND task_type_id = 6 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task ID 13: Blade sharpening
UPDATE tasks SET details = '{"blade_condition_before": "dull", "sharpening_method": "professional", "balance_checked": true}'::jsonb
WHERE item_id = 3 AND task_type_id = 7 AND completed_at = CURRENT_DATE - INTERVAL '10 months';

-- Task ID 14: Mid-season oil change
UPDATE tasks SET details = '{"hours_of_operation": 45, "oil_type": "10W-30", "prep_type": "mid-season"}'::jsonb
WHERE item_id = 3 AND task_type_id = 1 AND completed_at = CURRENT_DATE - INTERVAL '4 months';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
