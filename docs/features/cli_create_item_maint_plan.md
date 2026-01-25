# CLI: make item_id parameter optional in the create-item-maintenance-plan cli command

## Goal: the create-item-maintenance-plan cli should prompt the user to select an item from a list of items when the item_id is not provided as an input.

Context:
when launching the create-item-maintenance-plan cli command from the main menu, it does not ask the user to select an item.  it just gives the following error.

```
tracker: create-item-maintenance-plan
Error: Missing parameter: item_id
```

Instead, if there is no item_id passed as an input, allow the user to select the item from a list of all items owned by that user.
You can do this by making the item_id input optional in the create-item-maintenance-plan command.  If it is not provided, ask the user to select from a list of items.

We want to retain the ability to pass the item_id as an input.


## Prerequisites:
- understand the create-item-maintenance-plan cli command
- understand the GET /items/users/{user_id} API endpoint

## Process:
- launch the create-item-maintenance-plan cli command without providing any inputs
- query the GET /items/users/{user_id} API endpoint
- ask the user to select an item
- proceed with the create-item-maintenance-plan cli command using the selected item_id

## Testing:
- test the create-item-maintenance-plan cli command with a provided item_id.  It SHOULD NOT ask the user to select an item
- test the create-item-maintenance-plan cli command without a provided item_id.  It SHOULD ask the user to select an item






