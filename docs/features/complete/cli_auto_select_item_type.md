# CLI: Automatically select item type during maintenance template creation.

## Goal: When creating a new item type, and then choosing to create maintenance templates, the new item type should be automatically selected for the maintenance template

Context:
The issue arises during the following procedure:
- launch the create-item-type CLI script
- enter a name and description
- select `yes` to create maintenance templates for the new item type
- ISSUE: the cli script will ask the user to select from a list of item types.  It should remember the item type that was created earlier in the process and use this item type during this step.

## Prerequisites:
- understand the create-item-type CLI command
- understand the create-maintenance-template CLI command
- understand the POST /maintenance-templates API endpoint
- understand the POST /item-types API endpoint


## Testing:
- run the create-item-type cli command
- create a new item type
- select 'yes' to creating a new maintenance template
- CHECK: user should NOT be prompted to select an item type.  the item type that was created as part of this testing process should be automatically selected
