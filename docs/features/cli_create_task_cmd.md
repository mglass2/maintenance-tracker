# cli: Create task record

## goal
Create a cli command in the /cli service of the project that allows the user to create a task record by calling the POST /tasks endpoint of the API.  The task is associated with a given item that belongs to the active user (from header x-user-id).

## prerequisites
- consider the database structure in the /db service of the project
- consider the POST /tasks endpoint of the API.
- consider the POST /task-types endpoint of the API.

## process
- prompt the user to select an item that is owned by that user (from the user_id in header x-user-id).  The selected item's item_id is submitted as the item_id for the task
- prompt the user to select a task type from a list of task types that are present in the item_maintenance_plan table for the item_id selected in the previous step.  Also let the user make a selection for "Other", at which point:
    - the user will be prompted to enter the necessary information for creating a new task type - `name` and `description` (which is subsequently submitted to the API POST /task-types endpoint)
    - The `task_type_id` returned from the API call is used as the `task_type_id` for the new task.
- prompt the user to enter a `completed_at` date, present them with the appropriate format (yyyy-mm-dd) when asking.  Default should be the current day.
- prompt the user to enter `notes` about the task.
- prompt the user to enter the `cost` of the task
- if there is a item_maintenance_plan associated with this task, check to see if item_maintenance_plan.custom_interval JSONB field contains any data.  If there is:
    - The user should be prompted to enter data for an equivalent set of key(s) that exist in item_maintenance_plan.custom_interval.  the inputs submitted by the user should be submitted as the values for those keys on item.details. for example, a json structure of `{"mileage":5000, "hours":100}` would result in the user being prompted to enter inputs for `mileage` and `hours`.
    - package the keys and user-submitted values into json and use it for the tasks.details field.
- submit the information collected from the CLI to the POST /tasks endpoint of the API.
- show a confirmation or error message to the user.