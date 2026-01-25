# CLI: auto register user

## goal: if there is only one user created in the system, the operator should automatically be registered as that user when they open the CLI application.

## Process:
- When opening the application, get the list of current users.
- if there is only one user, automatically select that user for the CLI context
- otherwise, continue with the current behavior of asking the user to either create a user (if there are no users) or select a user (if there is more than one user)