-- Optional seed data for development and testing
-- This file is executed after 01-create-schema.sql if it exists

-- Example items
INSERT INTO items (name, description, purchase_date) VALUES
    ('Car - Toyota Camry', 'Daily commute vehicle', '2020-06-15'),
    ('Refrigerator - LG', 'Kitchen appliance', '2018-03-20'),
    ('HVAC System', 'Central heating and air conditioning', '2015-09-10')
ON CONFLICT (name) DO NOTHING;

-- Example maintenance task types
INSERT INTO maintenance_task_types (item_id, name, description, frequency_days, estimated_duration_minutes) VALUES
    (1, 'Oil Change', 'Change engine oil and filter', 10000, 30),
    (1, 'Tire Rotation', 'Rotate tires for even wear', 12000, 45),
    (2, 'Condenser Coil Cleaning', 'Clean condenser coils', 365, 60),
    (2, 'Filter Replacement', 'Replace air filter', 180, 20),
    (3, 'HVAC Inspection', 'Annual HVAC system inspection', 365, 120),
    (3, 'Refrigerant Check', 'Check refrigerant levels', 730, 90)
ON CONFLICT DO NOTHING;

-- Example task history
INSERT INTO task_history (item_id, task_type_id, completed_date, notes) VALUES
    (1, 1, '2025-01-15', 'Regular maintenance, all OK'),
    (1, 2, '2025-01-10', 'Tires rotated, pressure adjusted'),
    (2, 3, '2024-12-01', 'Condenser cleaned, working well'),
    (3, 5, '2024-06-15', 'Annual inspection passed')
ON CONFLICT DO NOTHING;
