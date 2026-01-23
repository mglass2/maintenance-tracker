## Task Details (JSONB Field)

The `tasks` table includes a `details` JSONB field for storing task-specific information that varies by item type and task type.

### Purpose
- Store flexible, semi-structured data without rigid schema
- Support different data requirements for different task types
- Enable querying on specific detail attributes

### Examples by Item Type

#### Automobile Tasks
- Oil changes: `{"mileage": 75000, "oil_type": "5W-30 Synthetic", "filter_brand": "Fram"}`
- Brake work: `{"front_pads_thickness_mm": 2, "rotor_condition": "replaced", "parts_replaced": ["front pads"]}`
- Air filter: `{"filter_types": ["cabin", "engine"], "brands": ["Bosch"]}`

#### House Tasks
- Roof inspection: `{"contractor": "ABC Roofing", "areas_inspected": ["shingles", "flashing"]}`
- Gutter cleaning: `{"debris_removed_lbs": 15, "downspouts_checked": true}`

#### Snowblower Tasks
- Oil change: `{"hours_of_operation": 45, "oil_type": "10W-30", "prep_type": "mid-season"}`
- Spark plugs: `{"gap_mm": 0.7, "spark_plug_brand": "NGK", "old_plug_condition": "worn"}`
- Blade sharpening: `{"sharpening_method": "professional", "balance_checked": true}`

### Querying JSONB Data

```sql
-- Find automobile tasks with specific mileage
SELECT * FROM tasks WHERE details->>'mileage' = '75000';

-- Find tasks containing mileage key
SELECT * FROM tasks WHERE details ? 'mileage';

-- Find tasks with specific oil_type
SELECT * FROM tasks WHERE details @> '{"oil_type": "5W-30 Synthetic Blend"}';

-- Extract mileage from all automobile tasks
SELECT id, completed_at, (details->>'mileage')::INTEGER as mileage
FROM tasks
WHERE details ? 'mileage'
ORDER BY (details->>'mileage')::INTEGER;
```

### Schema Flexibility
- Field is nullable (not all tasks require details)
- No rigid schema enforced at database level
- Application layer should validate structure using Pydantic models
