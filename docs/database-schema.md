# Database Schema

## Overview

The Maintenance Tracker database uses PostgreSQL and follows a normalized relational schema designed for efficient querying and maintenance forecasting.

## Entity Relationship Diagram

```
┌──────────────────┐
│     items        │
├──────────────────┤
│ id (PK)          │
│ name (UNIQUE)    │
│ description      │
│ purchase_date    │
│ created_at       │
│ updated_at       │
└────────┬─────────┘
         │ 1
         │
         │ N
         ├──────────────────────────────────┐
         │                                  │
         ▼ 1                           ▼ 1
┌──────────────────────────┐ ┌──────────────────────────┐
│ maintenance_task_types   │ │ task_history             │
├──────────────────────────┤ ├──────────────────────────┤
│ id (PK)                  │ │ id (PK)                  │
│ item_id (FK)             │ │ item_id (FK)             │
│ name                     │ │ task_type_id (FK)        │
│ description              │ │ completed_date           │
│ frequency_days           │ │ notes                    │
│ estimated_duration_min   │ │ created_at               │
│ created_at               │ │ updated_at               │
│ updated_at               │ └──────────────────────────┘
└──────────────────────────┘
         │ 1
         │
         │ N
         │
         ▼ 1
┌──────────────────────────┐
│ forecasted_schedule      │
├──────────────────────────┤
│ id (PK)                  │
│ item_id (FK)             │
│ task_type_id (FK)        │
│ scheduled_date           │
│ is_completed             │
│ completed_date           │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

## Table Definitions

### items

Represents items that require maintenance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique item identifier |
| name | VARCHAR(255) | NOT NULL, UNIQUE | Item name (e.g., "Car - Toyota Camry") |
| description | TEXT | | Item description |
| purchase_date | DATE | | When the item was purchased |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes**
- Primary key on `id`
- Unique constraint on `name`
- Index on `created_at` for sorting

**Example Data**
```sql
INSERT INTO items (name, description, purchase_date)
VALUES ('Car - Toyota Camry', 'Daily commute vehicle', '2020-06-15');
```

### maintenance_task_types

Defines types of maintenance tasks for items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique task type identifier |
| item_id | INTEGER | NOT NULL, FK | References items.id |
| name | VARCHAR(255) | NOT NULL | Task name (e.g., "Oil Change") |
| description | TEXT | | Task description |
| frequency_days | INTEGER | NOT NULL | How often task should be done (in days) |
| estimated_duration_minutes | INTEGER | | Estimated time to complete task |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Constraints**
- Foreign key to `items.id` with ON DELETE CASCADE
- Frequency must be positive in application logic

**Indexes**
- Primary key on `id`
- Index on `item_id` for lookups by item

**Example Data**
```sql
INSERT INTO maintenance_task_types
(item_id, name, description, frequency_days, estimated_duration_minutes)
VALUES (1, 'Oil Change', 'Change engine oil and filter', 10000, 30);
```

### task_history

Records completed maintenance tasks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique history record identifier |
| item_id | INTEGER | NOT NULL, FK | References items.id |
| task_type_id | INTEGER | NOT NULL, FK | References maintenance_task_types.id |
| completed_date | DATE | NOT NULL | When the task was completed |
| notes | TEXT | | Optional notes about the task |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Constraints**
- Foreign keys to `items.id` and `maintenance_task_types.id` with ON DELETE CASCADE
- Both foreign keys ensure referential integrity

**Indexes**
- Primary key on `id`
- Index on `item_id` for finding history by item
- Index on `completed_date` for time-based queries

**Example Data**
```sql
INSERT INTO task_history (item_id, task_type_id, completed_date, notes)
VALUES (1, 1, '2025-01-15', 'Regular maintenance, all OK');
```

### forecasted_schedule

Stores predicted future maintenance schedules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique schedule entry identifier |
| item_id | INTEGER | NOT NULL, FK | References items.id |
| task_type_id | INTEGER | NOT NULL, FK | References maintenance_task_types.id |
| scheduled_date | DATE | NOT NULL | Predicted task completion date |
| is_completed | BOOLEAN | DEFAULT FALSE | Whether the task has been done |
| completed_date | DATE | | Actual completion date (if completed) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Constraints**
- Foreign keys to `items.id` and `maintenance_task_types.id` with ON DELETE CASCADE
- `completed_date` must be >= `scheduled_date` if provided

**Indexes**
- Primary key on `id`
- Index on `item_id` for finding schedules by item
- Index on `scheduled_date` for time-based queries
- Index on `is_completed` for filtering pending tasks

**Example Data**
```sql
INSERT INTO forecasted_schedule
(item_id, task_type_id, scheduled_date, is_completed)
VALUES (1, 1, '2025-02-15', FALSE);
```

## Key Relationships

### Item → Task Types (1:N)
- An item can have multiple types of maintenance
- When an item is deleted, all its task types are cascade deleted

### Item → Task History (1:N)
- An item can have a history of many completed tasks
- When an item is deleted, all its history is cascade deleted

### Task Type → Task History (1:N)
- A task type can appear in multiple history records
- When a task type is deleted, all related history is cascade deleted

### Item → Forecasted Schedule (1:N)
- An item can have many forecasted maintenance dates
- When an item is deleted, all its forecasts are cascade deleted

### Task Type → Forecasted Schedule (1:N)
- A task type can appear in multiple forecast dates
- When a task type is deleted, all related forecasts are cascade deleted

## Cascade Delete Behavior

All foreign keys use `ON DELETE CASCADE` to maintain data consistency:

```
Deleting an item:
  - Removes all its task types
  - Removes all its task history
  - Removes all its forecasts

Deleting a task type:
  - Removes all related task history
  - Removes all related forecasts
```

## Indexes

Indexes optimize common query patterns:

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| items_pkey | items | id | Primary key lookup |
| items_name_unique | items | name | Prevent duplicate item names |
| idx_items_created_at | items | created_at | Sort items by creation |
| idx_maintenance_task_types_item_id | maintenance_task_types | item_id | Find tasks for item |
| idx_task_history_item_id | task_history | item_id | Find history for item |
| idx_task_history_completed_date | task_history | completed_date | Filter by completion date |
| idx_forecasted_schedule_item_id | forecasted_schedule | item_id | Find forecast for item |
| idx_forecasted_schedule_scheduled_date | forecasted_schedule | scheduled_date | Find upcoming tasks |
| idx_forecasted_schedule_is_completed | forecasted_schedule | is_completed | Filter pending tasks |

## Performance Considerations

### Query Patterns

**Get all upcoming maintenance for an item**
```sql
SELECT * FROM forecasted_schedule
WHERE item_id = ? AND scheduled_date >= NOW() AND is_completed = FALSE
ORDER BY scheduled_date;
```
- Uses: `idx_forecasted_schedule_item_id`, `idx_forecasted_schedule_is_completed`

**Get maintenance history for an item**
```sql
SELECT * FROM task_history
WHERE item_id = ?
ORDER BY completed_date DESC;
```
- Uses: `idx_task_history_item_id`, `idx_task_history_completed_date`

**Find last completion of a task type**
```sql
SELECT * FROM task_history
WHERE task_type_id = ?
ORDER BY completed_date DESC
LIMIT 1;
```
- Uses: Foreign key relationship

### Scaling

For large datasets (100,000+ records):
- Add partitioning on `completed_date` for task_history
- Consider archiving old task_history to separate table
- Add materialized views for frequently accessed forecast data
- Consider caching layer (Redis) for forecast results

## Initialization Scripts

Scripts in `db/init/` execute in alphabetical order:

1. **01-create-schema.sql**: Creates all tables and indexes
2. **02-seed-data.sql**: Populates example data (optional)

## Backup and Recovery

To back up the database:

```bash
docker exec maintenance-tracker-db pg_dump \
  -U maintenance_user maintenance_tracker \
  > backup.sql
```

To restore from backup:

```bash
docker exec -i maintenance-tracker-db psql \
  -U maintenance_user maintenance_tracker \
  < backup.sql
```

## Security

Database security measures:

- **Separate user account**: Uses `maintenance_user` (not superuser)
- **Password protection**: Requires password from `.env`
- **Network isolation**: Only accessible from Docker network
- **No external exposure**: Port only open to host for development

### Production Recommendations

- Implement row-level security (RLS)
- Use encrypted connections (SSL)
- Implement audit logging
- Regular automated backups
- Use secrets management for credentials
