# Data Model Logic

Don't permit hard deletes.  Instead, use an is_deleted flag to mark the item as deleted (which will then just hide it from any application logic).

### User
- user is a top level construct.
- user represents a human that owns the items being maintained.

### Item
- item is a top level construct.
- items are owned by one user at a time, or have no owner.

### Item Type
- item type defines what each item is. For example, a car and a house are types of items.
- each instance of an item has an item type.  

### Task
- task represents an instance of maintenance that is performed on an item.

### Task Type
- task type defines the type of maintenance performed.  For example, an oil change and brake pad change are task types.


## Maintenance Intervals
- task types may have different intervals for different cars.  for instance, one car might need an oil change every 3000 miles, while another car needs an oil change every 5000 miles.  we will define maintenance invervals/schedules at a later point.

### Task Type Schedule Logic
For a given item type, there exists a list of task types that serve as a maintenance template for all items of that item type.  The connection between the task type and the item type should not be stored directly on the task type table.  consider the following idea:
```
table: maintenance_template (or suggest a better one)
purpose: track the list of task types that need to be initialized for a given item's maintenance schedule.
fields: item_type_id, task_type_id, time_interval (the default length of time before this type of maintenance is performed), custom_interval (a nullable JSONB field that allows a custom maintenance interval to be defined - example: every 5000 miles for a vehicle, or every 100 hours for a snowblower, etc.)

table: item_maintenance_schedule
purpose: track the list of actual task types and their required intervals for an item.  This table allows us to make a forecast of future maintenance for a given item.  
additional logic: The user will be given the opportunity to accept the default intervals (from maintenance_template), or choose a different interval for each task type.  If there is a custom_interval defined in the maintenance_template table, the user MUST have the same type of custom_interval defined for the given item - task type combination in the item_maintenance_schedule table (example, oil change must have a mileage interval for a vehicle)
fields: item_id, task_type_id, time_interval (the default length of time before this type of maintenance is performed), custom_interval (a nullable JSONB field that allows a custom maintenance interval to be defined - example: every 5000 miles for a vehicle, or every 100 hours for a snowblower, etc.)
```






For a given item (by way of the item's item type), .  To track the actual maintenenace schedule for a given item, there will be a  
Every item has an item type.  