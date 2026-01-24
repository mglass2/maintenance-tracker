# API: Create item_maintenance_plan

Consider the item_maintenance_plan table in the /db service of the project.  In the API service of the project, create an API endpoint to create an item_maintenance_plan record.  It should accept the required fields (item_id, task_type_id, time_interval_days) and optionally the nullable fields (custom_interval) as inputs on the request.  The endpoint should return the full details of the newly created record, including the primary key id.
