# CLI: Create Item Maintenance Plan

Goal: Create a CLI command that guides users through creating customized maintenance plans for an item based on the maintenance templates defined for that item type.

## Summary

The `create-item-maintenance-plan` command:
1. Fetches the item and its type
2. Retrieves all maintenance templates for that item type
3. Shows the user each template and asks if they want to implement it
4. For templates they select, allows customization of intervals
5. Creates item_maintenance_plan records via the API
6. Displays a summary of what was created

## Usage

```bash
create-item-maintenance-plan <ITEM_ID>
```

### Example

```bash
$ create-item-maintenance-plan 5

Item: 2015 Toyota Camry
Setting up maintenance plan...

============================================================
Task Type: Oil Change
Default Interval: Every 90 days
Default Custom Interval: {"type": "mileage", "value": 3000, "unit": "miles"}
Implement this maintenance task? (yes/skip) [yes]:

Time interval in days (default: 90) [90]: 120

Custom Interval Configuration:
The template defines these custom intervals:
  type (default: mileage) [mileage]:
  value (default: 3000) [3000]: 5000
  unit (default: miles) [miles]:

✓ Created: Oil Change

============================================================
Task Type: Tire Rotation
Default Interval: Every 180 days
Implement this maintenance task? (yes/skip) [yes]: skip

⊘ Skipped: Tire Rotation

============================================================
Task Type: Air Filter Replacement
Default Interval: Every 365 days
Implement this maintenance task? (yes/skip) [yes]:

Time interval in days (default: 365) [365]:

✓ Created: Air Filter Replacement

============================================================
Maintenance Plan Setup Complete

✓ Created 2 plan(s):
  • Oil Change
  • Air Filter Replacement

⊘ Skipped 1 plan(s):
  • Tire Rotation
```

## Process Flow

### 1. Fetch Item Details
Retrieves the item record to get the item_type_id. If the item doesn't exist, returns an error.

**API Call**: `GET /items/{item_id}`

### 2. Fetch Maintenance Templates
Gets all active maintenance templates for the item's type. Templates include the default time interval and any custom interval configuration.

**API Call**: `GET /maintenance_templates/item_types/{item_type_id}`

### 3. Check Existing Plans
Retrieves any existing maintenance plans for the item to avoid creating duplicates.

**API Call**: `GET /item_maintenance_plans/items/{item_id}`

### 4. Process Each Template
For each maintenance template, the user is presented with:
- The task type name
- The default time interval
- Any default custom interval configuration

The user can:
- **Accept** (yes/y or press Enter): Proceed to customization
- **Skip** (skip/s/no/n): Skip this template

### 5. Customize Intervals
If the user accepts a template:

**Time Interval**: User can override the default number of days between maintenance tasks. Must be a positive integer.

**Custom Intervals**: If the template has custom intervals (like mileage-based intervals), the user can customize each field. The system preserves the data type from the template (integers stay integers, strings stay strings).

### 6. Create Plan
Once customized, the maintenance plan is created via the API.

**API Call**: `POST /item_maintenance_plans`

Payload:
```json
{
  "item_id": 5,
  "task_type_id": 1,
  "time_interval_days": 120,
  "custom_interval": {
    "type": "mileage",
    "value": 5000,
    "unit": "miles"
  }
}
```

### 7. Display Summary
After all templates are processed, shows:
- Count of successfully created plans
- List of created task types
- Count of skipped plans
- List of skipped task types

## Prerequisites & Dependencies

### Required API Endpoints

- `GET /items/{item_id}` - Fetch item details
- `GET /maintenance_templates/item_types/{item_type_id}` - Fetch templates for item type
- `GET /item_maintenance_plans/items/{item_id}` - Check for existing plans
- `POST /item_maintenance_plans` - Create new maintenance plan

### Database Tables

- `items` - Item records with item_type_id
- `maintenance_template` - Templates with time_interval_days and custom_interval
- `item_maintenance_plan` - Records being created
- `task_types` - Task type names (joined for display)

## Error Handling

- **Item not found**: Returns error if item_id doesn't exist or is deleted
- **No templates**: Returns error if item type has no templates
- **API connection errors**: Handles connection timeouts and API unavailability
- **Duplicate plans**: Skips templates that already have plans for the item
- **Validation errors**: Validates user input for intervals (must be positive integers)

## Behavior Notes

- **Default values**: All prompts have sensible defaults (yes for template selection, template values for intervals)
- **Type preservation**: Custom interval values preserve their type from the template
- **Soft deletes**: Only considers non-deleted records (is_deleted = false)
- **Case insensitive**: Template selection accepts yes/no in any case
- **Partial success**: Continues processing if one plan creation fails