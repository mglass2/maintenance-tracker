-- ============================================================================
-- Maintenance Tracker Seed Data
-- ============================================================================
-- Sample test data for development and testing.
-- This creates a realistic dataset with maintenance history spanning 12 months.
-- ============================================================================

-- ============================================================================
-- USERS
-- ============================================================================
INSERT INTO users (name, email) VALUES
('Test User', 'test@example.com');

-- ============================================================================
-- ITEM TYPES
-- ============================================================================
-- IMPORTANT: These are the exact three types specified in requirements
INSERT INTO item_types (name, description) VALUES
('Automobile', 'Motor vehicles including cars, trucks, and motorcycles'),
('House', 'Residential buildings and properties'),
('Snowblower', 'Snow removal equipment');

-- ============================================================================
-- TASK TYPES
-- ============================================================================
-- Common maintenance tasks across different item types
INSERT INTO task_types (name, description) VALUES
('Oil Change', 'Replace engine oil and oil filter'),
('Air Filter Replacement', 'Replace air filter element'),
('Brake Inspection', 'Inspect brake pads, rotors, and fluid'),
('Roof Inspection', 'Inspect roof for damage, leaks, and wear'),
('Gutter Cleaning', 'Remove debris from gutters and downspouts'),
('Spark Plug Replacement', 'Replace spark plugs'),
('Blade Sharpening', 'Sharpen cutting blades');

-- ============================================================================
-- ITEMS
-- ============================================================================
-- Sample items owned by the test user
INSERT INTO items (user_id, item_type_id, name, description, acquired_at) VALUES
(1, 1, '2015 Honda Accord', 'Silver sedan, 4-door, automatic transmission', '2020-06-15'),
(1, 2, 'Main House', '3-bedroom colonial built in 1995', '2018-03-20'),
(1, 3, 'Toro Snow Blower', 'Two-stage snow blower, 24-inch width', '2019-11-10');

-- ============================================================================
-- TASKS
-- ============================================================================
-- Maintenance history spanning the last 12 months
-- Tasks are ordered by completed_at date (oldest first)

-- Tasks for automobile (2015 Honda Accord)
-- Oil changes approximately every 3 months
INSERT INTO tasks (item_id, task_type_id, completed_at, cost, notes) VALUES
(1, 1, CURRENT_DATE - INTERVAL '11 months', 45.99, 'Regular oil change with synthetic blend'),
(1, 1, CURRENT_DATE - INTERVAL '8 months', 47.50, 'Oil change and tire rotation'),
(1, 2, CURRENT_DATE - INTERVAL '6 months', 35.00, 'Replaced cabin and engine air filters'),
(1, 3, CURRENT_DATE - INTERVAL '6 months', 0.00, 'Brake inspection - passed, no work needed'),
(1, 1, CURRENT_DATE - INTERVAL '5 months', 45.99, NULL),
(1, 1, CURRENT_DATE - INTERVAL '2 months', 48.75, 'Oil change, topped off fluids'),
(1, 3, CURRENT_DATE - INTERVAL '1 month', 285.00, 'Replaced front brake pads and rotors');

-- Tasks for house (Main House)
INSERT INTO tasks (item_id, task_type_id, completed_at, cost, notes) VALUES
(2, 4, CURRENT_DATE - INTERVAL '10 months', 150.00, 'Annual roof inspection - some minor repairs needed'),
(2, 5, CURRENT_DATE - INTERVAL '9 months', 0.00, 'Fall gutter cleaning - removed leaves and debris'),
(2, 5, CURRENT_DATE - INTERVAL '3 months', 0.00, 'Spring gutter cleaning');

-- Tasks for snowblower (Toro Snow Blower)
-- Pre-season and mid-season maintenance
INSERT INTO tasks (item_id, task_type_id, completed_at, cost, notes) VALUES
(3, 1, CURRENT_DATE - INTERVAL '10 months', 22.50, 'Pre-season oil change'),
(3, 6, CURRENT_DATE - INTERVAL '10 months', 15.00, 'Replaced spark plug before winter'),
(3, 7, CURRENT_DATE - INTERVAL '10 months', 12.00, 'Sharpened blades for winter season'),
(3, 1, CURRENT_DATE - INTERVAL '4 months', 22.50, 'Mid-season oil check and change');

-- ============================================================================
-- SEED DATA COMPLETE
-- ============================================================================
-- Summary:
--   - 1 user
--   - 3 item types (automobile, house, snowblower)
--   - 7 task types
--   - 3 items
--   - 15 tasks with maintenance history spanning 12 months
-- ============================================================================