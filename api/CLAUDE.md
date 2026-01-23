# Good CLI design
- if the operator provides an empty input for a prompt, the CLI should preseent an appropriate error message and then reprompt the operator
- 

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
- CLI: utility/process to register the current session to a given user in the system.  this user identity will be passed to the API with each request automatically.
- CLI: create user command
- CLI: change user command that presents the user with a list of other users and lets them pick.
- CLI: when launching the cli, check how many current users there are.  if there are 0, launch the create-user command.  if there is one, register the current session for that user.  if there are multiple users, launch the change user command. 
- API: create item_maintenance_plan record (actual maintenance plan for a given item / task type combination)
- API: get future predicted task list for item (all tasks or by additive filter list for task_type)