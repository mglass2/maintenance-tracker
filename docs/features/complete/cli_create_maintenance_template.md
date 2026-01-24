# CLI: Create Maintenance Template

## Overview

The `create-maintenance-template` command guides users through creating maintenance template records. A maintenance template defines the standard maintenance intervals for a specific combination of item type and task type.

## Command

```bash
create-maintenance-template
```

## Prerequisites

- Database table `maintenance_template` exists with proper schema
- POST `/maintenance_templates` API endpoint is available
- GET `/item_types` API endpoint is available
- GET `/task_types` API endpoint is available
- GET `/maintenance_templates/item_types/{item_type_id}` API endpoint is available

## Workflow

The command guides the user through these steps:

1. **Select Item Type** - Display all available item types and let user select one
2. **View Existing Templates** - Display any existing maintenance templates for the selected item type
3. **Select Task Type** - Display all available task types and let user select one
4. **Set Time Interval** - Collect required `time_interval_days` field with validation (must be positive integer)
5. **Add Custom Fields** (Optional) - Loop to collect optional custom interval key-value pairs:
   - Ask "Would you like to save any other information about this maintenance template?"
   - If yes, get field name and value, auto-convert types (int → int, numeric → float, else string)
   - Repeat until user declines
6. **Create Template** - Submit to POST `/maintenance_templates` endpoint
7. **Display Result** - Show success confirmation with template details or error message

## Example Session

```
$ create-maintenance-template

Available Item Types:
  1. Automobile - Motor vehicles including cars, trucks, and motorcycles
  2. Car - Automobile
  3. House - Residential buildings and properties
  4. Snowblower - Snow removal equipment

Select an item type (1-4): 3

No existing templates for House

============================================================

Available Task Types:
  1. Air Filter Replacement - Replace air filter element
  2. Blade Sharpening - Sharpen cutting blades
  3. Brake Inspection - Inspect brake pads, rotors, and fluid
  4. Gutter Cleaning - Remove debris from gutters and downspouts
  5. Oil Change - Replace engine oil and oil filter
  6. Roof Inspection - Inspect roof for damage, leaks, and wear

Select a task type (1-6): 4

Time interval in days (how often should this maintenance be performed): 365

Would you like to save any other information about this maintenance template? (yes/no) [no]: yes
Enter the name for the information (or press Enter to finish): contractor_cost
What value would you like to submit for contractor_cost?: 250
✓ Added: contractor_cost = 250

Would you like to save any other information about this maintenance template? (yes/no) [no]: no

✓ Success: Maintenance template created successfully!

Template Details:
  ID:                1
  Item Type:         House
  Task Type:         Gutter Cleaning
  Interval (days):   365
  Custom Interval:   {"contractor_cost": 250}
  Created:           2026-01-24T22:49:25.022784
```

## Error Handling

- **Empty Selection** - Prompts user to enter a valid selection if they leave it blank
- **Invalid Selection** - Shows error with valid range and re-prompts
- **Invalid Interval** - Must be positive integer; validation message shown
- **Duplicate Template** - Returns 409 error with message about existing template for same item/task combo
- **API Connection Error** - Clear message when API is unavailable
- **Server Error** - Graceful error message with guidance to retry later
- **Resource Not Found** - 404 errors handled with appropriate messaging

## Field Normalization

Field names are normalized to lowercase with underscores:
- "Mileage Threshold" → `mileage_threshold`
- "Contractor Cost" → `contractor_cost`
- "Oil capacity" → `oil_capacity`

## Type Auto-Conversion

Custom interval values are automatically converted:
- "15000" → 15000 (integer)
- "25.5" → 25.5 (float)
- "Every 3 months" → "Every 3 months" (string)

## Implementation Details

- **File**: `/cli/src/commands/maintenance_template.py`
- **Command Name**: `create-maintenance-template` (hyphenated for CLI consistency)
- **Function**: `create_maintenance_template()`
- **Registered In**: `/cli/src/main.py`

## Testing

The command has been tested with:
- ✓ Basic template creation with required fields
- ✓ Duplicate detection (409 conflict error)
- ✓ Custom interval field collection and type conversion
- ✓ Error handling for all error scenarios
- ✓ Item type selection and display
- ✓ Task type selection and display
- ✓ Existing template display

## Design Decisions

1. **Item Type Selection First** - Select item type before task types to show context-relevant existing templates
2. **Existing Templates Display** - Show current templates to help user understand what's already configured
3. **Automatic Type Conversion** - No need for user to specify type; system intelligently converts values
4. **Field Name Normalization** - Simple lowercase + underscore conversion; no complex translation dictionaries
5. **Optional Custom Interval** - User-friendly loop that asks repeatedly if more fields needed
6. **Specific Error Messages** - Clear guidance for each error scenario (especially 409 duplicate)