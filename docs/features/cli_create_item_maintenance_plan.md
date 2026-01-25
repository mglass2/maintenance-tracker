when launching the create-item-maintenance-plan cli command from the main menu, it does not ask the user to select an item.  it just gives the following error.

```
tracker: create-item-maintenance-plan
Error: Missing parameter: item_id
```

Instead, if there is no item_id passed as an input, allow the user to select the item from a list of all items owned by the current user.