# Rules
- Do not write code that hard deletes records.  Instead, prefer to use soft deletes via is_deleted flags.

# Application Logic

## User
A user is a top level construct of the application.  
user enters tasks that are performed on items.  
The operator of the application will typically be the currently active user.

## Item
An item is a top level construct of the application.  
Items are owned by one user at a time, but users may transfer ownership of an item.
Each item is classified as a certain type.  For example, a car and a house are types of items.
Each item type (car/house/etc) has a predefined set of tasks that apply to that type of item.  For example, a cars need to have an oil change, new brake pads, and inspections; but houses need roof replacement, water filter change, or hot water heater flushed.

## Task
A task is performed on an item.  For example, an Oil Change is a task that can be performed on a car.
Tasks may need to be performed more than once on a given item.  For example, cars need to have their oil changed based on mileage OR time since the last oil change.
Each type of task is either one-time, or recurring.  The 


# Future Features Todo (endpoints)
- create maintenance_template record (default maintenance interval for a task type / item type combination)
- create item_maintenance_plan record (actual maintenance plan for a given item / task type combination)
- get item list for user
- get completed task list for item
- get future predicted task list for item (all tasks or by additive filter list)
- 