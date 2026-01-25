# DB: add item_type_id to the task_types table

## Goal: we want to be able to classify task types according to item type, even if a maintenance_template is not established for that task type - item type connection yet.

## Context:
- add item_type_id (non-nullable) to the task_types table
- update the POST /task_types API endpoint to expect item_type_id to be submitted.
- update the GET /task_types API endpoint to allow an optional filter for item_type_id
- in the create-maintenance-template CLI command, the user is prompted to select an item type, and is then shown all task types.  The list of task types shown to the user should now only display those associated with the selected item_type.
- places where we connect item type and task type through the maintenance_template table should not be altered, since there is already a connection established between item_type_id and task_type_id in those locations.

## Prerequisites:
- consider the database structure of the project in the /db folder
- consider the task type API endpoints in the API service of the project, the routes can be found at api/src/routes/task_types.py
- consider the create-maintenance-template CLI command
- ask me to select an appropriate item_type for each task_type that is already in the database so that you know how to update the existing task_type rows

## testing
- update the tests for the POST /task-types endpoint to reflect submitting item_type_id
- update the tests for the GET /task-types endpoint to reflect optionally filtering by item_type_id