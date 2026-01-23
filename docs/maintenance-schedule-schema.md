# Maintenance Schedule Database Schema Proposal

This document proposes a database schema to implement the "Maintenance Intervals" and "Task Type Schedule Logic" concepts described in `/db/CLAUDE.md`.

## Overview

The proposed schema introduces two new tables to support dynamic maintenance scheduling:

1. **`maintenance_template`** - Defines which task types apply to each item type, with default maintenance intervals
2. **`item_maintenance_plan`** - Tracks the actual maintenance intervals for specific items (can override template defaults)

This design allows:
- Reusable maintenance templates for item types
- Per-item customization of maintenance intervals
- Support for both time-based (days) and custom (mileage, hours, etc.) interval types
- Forecasting of future maintenance

## SQL Schema

```sql
-- ============================================================================
-- TABLE: maintenance_template
-- ============================================================================
-- Defines the default maintenance schedule for each item type.
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
  -- Ensure each task type appears only once per item type
  CONSTRAINT maintenance_template_unique_per_item_type
    UNIQUE (item_type_id, task_type_id) WHERE is_deleted = FALSE,
  -- Ensure time_interval is positive
  CONSTRAINT time_interval_positive CHECK (time_interval_days > 0)
);

COMMENT ON TABLE maintenance_template IS
  'Defines default maintenance schedules for item types. ' ||
  'Serves as a template when creating new items of that type.';

COMMENT ON COLUMN maintenance_template.item_type_id IS
  'The item type this maintenance template applies to';

COMMENT ON COLUMN maintenance_template.task_type_id IS
  'The task type in this maintenance schedule';

COMMENT ON COLUMN maintenance_template.time_interval_days IS
  'Default number of days between maintenance tasks (must be positive)';

COMMENT ON COLUMN maintenance_template.custom_interval IS
  'JSONB field for custom interval definitions (e.g., mileage, hours). ' ||
  'Example: {"type": "mileage", "value": 5000, "unit": "miles"} or ' ||
  '{"type": "hours", "value": 100, "unit": "hours"}';

COMMENT ON COLUMN maintenance_template.is_deleted IS
  'Soft delete flag - TRUE means deleted, FALSE means active';


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
  -- Ensure each task type appears only once per item
  CONSTRAINT item_maintenance_plan_unique_per_item
    UNIQUE (item_id, task_type_id) WHERE is_deleted = FALSE,
  -- Ensure time_interval is positive
  CONSTRAINT item_time_interval_positive CHECK (time_interval_days > 0)
);

COMMENT ON TABLE item_maintenance_plan IS
  'Tracks the actual maintenance intervals for a specific item. ' ||
  'Allows customization of intervals per item (overriding template defaults). ' ||
  'Used for forecasting future maintenance.';

COMMENT ON COLUMN item_maintenance_plan.item_id IS
  'The item this maintenance schedule applies to';

COMMENT ON COLUMN item_maintenance_plan.task_type_id IS
  'The task type in this maintenance schedule';

COMMENT ON COLUMN item_maintenance_plan.time_interval_days IS
  'Number of days between maintenance tasks for this item (must be positive)';

COMMENT ON COLUMN item_maintenance_plan.custom_interval IS
  'JSONB field for custom interval definitions specific to this item. ' ||
  'Example: {"type": "mileage", "value": 3000, "unit": "miles"} for a car ' ||
  'with custom mileage-based oil change interval';

COMMENT ON COLUMN item_maintenance_plan.is_deleted IS
  'Soft delete flag - TRUE means deleted, FALSE means active';


-- ============================================================================
-- INDEXES
-- ============================================================================

-- Foreign key indexes for efficient joins
CREATE INDEX idx_maintenance_template_item_type_id
  ON maintenance_template(item_type_id);
CREATE INDEX idx_maintenance_template_task_type_id
  ON maintenance_template(task_type_id);

CREATE INDEX idx_item_maintenance_plan_item_id
  ON item_maintenance_plan(item_id);
CREATE INDEX idx_item_maintenance_plan_task_type_id
  ON item_maintenance_plan(task_type_id);

-- Soft delete indexes
CREATE INDEX idx_maintenance_template_is_deleted
  ON maintenance_template(is_deleted);
CREATE INDEX idx_item_maintenance_plan_is_deleted
  ON item_maintenance_plan(is_deleted);

-- Composite index for common query patterns:
-- "Get all task types for a given item that need to be scheduled"
CREATE INDEX idx_item_maintenance_plan_item_id_is_deleted
  ON item_maintenance_plan(item_id, is_deleted);

-- "Get all items of a type that have a given task type scheduled"
CREATE INDEX idx_maintenance_template_item_type_task_type
  ON maintenance_template(item_type_id, task_type_id) WHERE is_deleted = FALSE;
```

## Table Descriptions

### maintenance_template

**Purpose**: Define default maintenance schedules for each item type.

**When Used**:
- When creating a new item type, administrators define which task types apply to it
- When a new item is created, the template is used to initialize its maintenance schedule

**Fields**:
- `id`: Primary key
- `item_type_id`: Links to the item type (e.g., "automobile", "house")
- `task_type_id`: Links to the task type (e.g., "Oil Change", "Roof Inspection")
- `time_interval_days`: Default number of days between maintenance tasks
  - Example: 180 days for an oil change
  - Must be positive (checked by constraint)
- `custom_interval`: Optional JSONB field for non-time-based intervals
  - Example: `{"type": "mileage", "value": 5000, "unit": "miles"}` for oil changes based on mileage
  - Example: `{"type": "hours", "value": 100, "unit": "hours"}` for snowblower maintenance
  - `null` if the task type only uses time-based intervals
- `is_deleted`: Soft delete flag
- `created_at`, `updated_at`: Audit timestamps

**Key Constraints**:
- `(item_type_id, task_type_id)` must be unique (one entry per task type per item type)
- `time_interval_days` must be positive
- Foreign keys prevent deleting referenced item types or task types

### item_maintenance_plan

**Purpose**: Track actual maintenance intervals for a specific item (can override template defaults).

**When Used**:
- When a new item is created, entries are populated from the template
- The user can modify these entries to customize intervals for their specific item
- Used to forecast future maintenance dates

**Fields**:
- `id`: Primary key
- `item_id`: Links to the specific item
- `task_type_id`: Links to the task type
- `time_interval_days`: Number of days between maintenance tasks for THIS item
  - Can override the template default if the item has different requirements
  - Example: User's car might need oil changes every 3000 miles (≈ 60 days at typical driving)
  - Another user's car might need them every 5000 miles (≈ 100 days)
- `custom_interval`: Item-specific custom interval (must match template requirements)
  - If the template defines `custom_interval` for a task type, this field MUST be set
  - Example: If template says oil changes can use mileage, this must specify the mileage for THIS item
  - Can differ from the template if the item has different specifications
- `is_deleted`: Soft delete flag
- `created_at`, `updated_at`: Audit timestamps

**Key Constraints**:
- `(item_id, task_type_id)` must be unique (one entry per task type per item)
- `time_interval_days` must be positive
- Foreign keys prevent deleting referenced items or task types
- Custom interval validation (application-level): if a template requires a custom interval type, the schedule entry must provide it

## Data Flow & Logic

### Creating an Item Type with Maintenance Template

```
1. Admin creates ItemType (e.g., "Automobile")
2. Admin creates TaskTypes (e.g., "Oil Change", "Tire Rotation", "Brake Inspection")
3. Admin creates MaintenanceTemplate entries linking Automobile to each TaskType
   with default intervals and optional custom interval specifications

Example:
  - Automobile + Oil Change: 180 days, custom_interval: {type: "mileage", unit: "miles"}
  - Automobile + Tire Rotation: 360 days, custom_interval: null (time-based only)
  - Automobile + Brake Inspection: 730 days, custom_interval: null
```

### Creating a New Item

```
1. User creates Item (e.g., "My Toyota Camry", type: Automobile)
2. System queries MaintenanceTemplate for all tasks for Automobile (is_deleted = FALSE)
3. System creates ItemMaintenanceSchedule entries populated from template:
   - Oil Change: 180 days, custom_interval: {type: "mileage", unit: "miles"} (copied from template)
   - Tire Rotation: 360 days, custom_interval: null (copied from template)
   - Brake Inspection: 730 days, custom_interval: null (copied from template)
4. User optionally customizes intervals:
   - "My car gets oil changes every 5000 miles" → update custom_interval to {type: "mileage", value: 5000, unit: "miles"}
   - "I'm more aggressive with brakes, check every 6 months" → update time_interval_days to 180
```

### Forecasting Future Maintenance

```
Query: "What maintenance is due for my car in the next 90 days?"

1. Get ItemMaintenanceSchedule for the item (is_deleted = FALSE)
2. For each schedule entry:
   - If time_interval_days based: calculate next_due_date = last_task.completed_at + time_interval_days
   - If custom_interval based: use application logic to calculate next due date
     (e.g., if mileage-based, need to know current mileage from the item)
3. Filter for tasks with next_due_date <= today + 90 days
4. Return as maintenance forecast
```

## Custom Interval Examples

### Example 1: Vehicle Oil Change (Mileage-Based)

**MaintenanceTemplate Entry**:
```json
{
  "item_type_id": 1,        // Automobile
  "task_type_id": 5,        // Oil Change
  "time_interval_days": 180, // fallback: every 6 months if miles aren't tracked
  "custom_interval": {
    "type": "mileage",
    "unit": "miles",
    "description": "Oil change needed"
  }
}
```

**ItemMaintenanceSchedule Entry** (User's specific car):
```json
{
  "item_id": 42,            // My Toyota Camry
  "task_type_id": 5,        // Oil Change
  "time_interval_days": 180,
  "custom_interval": {
    "type": "mileage",
    "value": 5000,          // Every 5000 miles
    "unit": "miles",
    "last_value": 45000,    // Last task at 45000 miles
    "next_due_value": 50000 // Next due at 50000 miles
  }
}
```

### Example 2: House Roof Inspection (Time-Based Only)

**MaintenanceTemplate Entry**:
```json
{
  "item_type_id": 2,        // House
  "task_type_id": 8,        // Roof Inspection
  "time_interval_days": 365, // Annual inspection
  "custom_interval": null    // No custom interval needed
}
```

**ItemMaintenanceSchedule Entry** (User's house):
```json
{
  "item_id": 10,            // My house
  "task_type_id": 8,        // Roof Inspection
  "time_interval_days": 365, // Every year
  "custom_interval": null
}
```

### Example 3: Snowblower (Hours-Based)

**MaintenanceTemplate Entry**:
```json
{
  "item_type_id": 3,        // Snowblower
  "task_type_id": 12,       // Spark Plug Replacement
  "time_interval_days": 365, // fallback: annual
  "custom_interval": {
    "type": "hours",
    "unit": "hours",
    "description": "Operating hours"
  }
}
```

**ItemMaintenanceSchedule Entry**:
```json
{
  "item_id": 78,            // My snowblower
  "task_type_id": 12,       // Spark Plug Replacement
  "time_interval_days": 365,
  "custom_interval": {
    "type": "hours",
    "value": 50,           // Every 50 operating hours
    "unit": "hours",
    "last_value": 230,     // Last replacement at 230 hours
    "next_due_value": 280  // Next due at 280 hours
  }
}
```

## Application Logic Requirements

### When Creating an Item

1. Query `MaintenanceTemplate` for the item's type
2. For each template entry, create an `ItemMaintenanceSchedule` entry with:
   - `time_interval_days` copied from template
   - `custom_interval` copied from template (or null)
3. If template's `custom_interval` is not null, user MUST provide a value

### When Validating Custom Intervals

1. If `MaintenanceTemplate.custom_interval` is not null:
   - `ItemMaintenanceSchedule.custom_interval` MUST also be not null
   - The interval type MUST match (e.g., if template says "mileage", schedule must specify mileage)
   - The interval must have required fields (type, unit, value)

2. If `MaintenanceTemplate.custom_interval` is null:
   - `ItemMaintenanceSchedule.custom_interval` SHOULD be null
   - Only use `time_interval_days` for forecasting

### When Forecasting Maintenance

For each `ItemMaintenanceSchedule` entry:

1. Find the most recent completed task of that type for the item
2. If no task exists, next due date = item.acquired_at + time_interval_days
3. If custom_interval is present:
   - Use custom interval logic (application-specific)
   - Example: For mileage, next_due = last_task.custom_data.mileage + custom_interval.value
4. If only time_interval_days:
   - next_due = last_task.completed_at + time_interval_days days

## Soft Delete Behavior

All tables use soft deletes (is_deleted flag):

- **Delete a MaintenanceTemplate**: Set is_deleted = TRUE
  - Existing `ItemMaintenanceSchedule` entries remain (with their data)
  - New items of that type won't get this template entry

- **Delete an ItemMaintenanceSchedule**: Set is_deleted = TRUE
  - Item still exists, but forecasting won't include this task type
  - Historical tasks remain in `tasks` table
  - User can un-delete to restore forecasting

## Migration Strategy

To add these tables to an existing database:

1. Create the `maintenance_template` table
2. Create the `item_maintenance_plan` table
3. Optionally, populate both tables with initial data for existing items:
   ```sql
   -- For each existing item, insert default schedules based on its item type's template
   INSERT INTO item_maintenance_plan (item_id, task_type_id, time_interval_days, custom_interval)
   SELECT
     i.id,
     mt.task_type_id,
     mt.time_interval_days,
     mt.custom_interval
   FROM items i
   JOIN maintenance_template mt ON i.item_type_id = mt.item_type_id
   WHERE i.is_deleted = FALSE
     AND mt.is_deleted = FALSE;
   ```

## Alternative Naming Suggestions

- `maintenance_template` → `task_type_schedules` or `item_type_maintenance_tasks`
- `item_maintenance_plan` → `item_task_schedules` or `item_maintenance_plan`

The names in this proposal follow the pattern:
- `maintenance_template` = template/default schedules
- `item_maintenance_plan` = actual/instance schedules for items

## Related Queries

### Query 1: Get all task types for an item type (template)
```sql
SELECT mt.*, tt.name as task_name
FROM maintenance_template mt
JOIN task_types tt ON mt.task_type_id = tt.id
WHERE mt.item_type_id = $1
  AND mt.is_deleted = FALSE
  AND tt.is_deleted = FALSE;
```

### Query 2: Get maintenance schedule for a specific item
```sql
SELECT ims.*, tt.name as task_name
FROM item_maintenance_plan ims
JOIN task_types tt ON ims.task_type_id = tt.id
WHERE ims.item_id = $1
  AND ims.is_deleted = FALSE
  AND tt.is_deleted = FALSE;
```

### Query 3: Find overdue maintenance for an item
```sql
SELECT
  ims.id,
  tt.name as task_name,
  MAX(t.completed_at) as last_completed,
  ims.time_interval_days,
  MAX(t.completed_at) + (ims.time_interval_days || ' days')::INTERVAL as next_due
FROM item_maintenance_plan ims
JOIN task_types tt ON ims.task_type_id = tt.id
LEFT JOIN tasks t ON ims.item_id = t.item_id
  AND ims.task_type_id = t.task_type_id
  AND t.is_deleted = FALSE
WHERE ims.item_id = $1
  AND ims.is_deleted = FALSE
GROUP BY ims.id, tt.name, ims.time_interval_days
HAVING MAX(t.completed_at) + (ims.time_interval_days || ' days')::INTERVAL <= NOW();
```

## Summary

This schema enables:

✅ Reusable maintenance templates per item type
✅ Per-item customization of intervals
✅ Support for multiple interval types (time, mileage, hours, etc.)
✅ Soft delete compliance
✅ Efficient forecasting queries
✅ Historical tracking of all maintenance tasks
✅ Scalability for future custom interval types
