# CLI: Create item type command

# Goal: Create a CLI Command that allows the user to create an item type record

## Prerequisites
- consider the item_types table in the /db section of the project.
- consider the POST /item_types endpoint in the API section of the project

## Process
- Collect the required name and optional description from the user
- submit the name and description to the POST /item_types endpoint
- give the user a confirmation of the item type
- ask the user if they would like to launch the create-maintenance-template CLI Command for the newly created item type.  if so, launch that command to allow the user to create maintenance plans for that item type.