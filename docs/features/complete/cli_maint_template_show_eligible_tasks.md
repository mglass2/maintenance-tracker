# CLI: create-maintenance-template command - only show task types that don't have a maintenance plan

## Goal: in the create-maintenance-template command, we show a list of "Available Task Types", which contains all task types associated with the selected item type.  We only want to show task types that DON'T have a maintenance_template record connected to the selected item type.

## Context:
- consider the create-maintenance-template cli command
- consider the maintenance-template, task-types, and item-types db tables
- consider the API endpoints that are called within the create-maintenance-template cli command

## Process:
When gathering the list of task types for the "Available Task Types:" menu, filter out the task types that have a maintenance_template record associated with the item type that was selected earlier in the command process.

## Testing:
- test that task types that have a maintenance_template record associated with the item type that was selected earlier in the command process are filtered out of the "Available Task Types:" menu
