-- Add details JSONB field to items table
ALTER TABLE items ADD COLUMN details JSONB;

COMMENT ON COLUMN items.details IS 'Item-type-specific metadata stored as JSON (e.g., mileage for vehicles, square footage for houses)';
