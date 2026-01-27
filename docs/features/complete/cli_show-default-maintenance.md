# CLI: Show Task Types for all item types

## Goal: Create a CLI command called show-default-maintenance that shows a list of all item types, and the task types associated with each item type

## Context:
Allow users to see all the item types, and the task types associated with those item types.
item_type and task_type relationship is defined in the maintenance_template table.
display should look like this
```
Item Type 1:
    [Task Type Name] - [time_interval_days] - [custom_interval]
    [Task Type Name] - [time_interval_days] - [custom_interval]

Item Type 2:
    [Task Type Name] - [time_interval_days] - [custom_interval]
    [Task Type Name] - [time_interval_days] - [custom_interval]
    [Task Type Name] - [time_interval_days] - [custom_interval]
    [Task Type Name] - [time_interval_days] - [custom_interval]

...
```

## Prerequisites:
- understand the task_types, item_types, maitenance_templates db tables.
- understand the GET API endpoints in api/src/routes/item_types.py, api/src/routes/task_types.py, api/src/routes/maintenance_templates.py

## Testing:
- confirm that the command shows all the item type - task type relationships defined in the maintenance_template table.
- confirm that the command does not show any the item types or task types that are not present in the maintenance_template table.