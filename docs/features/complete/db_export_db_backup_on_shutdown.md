# CLI/API/DB: Database backup process

## Goal: create a database backup to a SQL file every time the application is shut down.  also maintain/rotate the existing db backups

## Context:
Every time the user exits the application, export the entire database schema and data to a SQL file on a shared volume in the API service of docker.
Name the files with a timestamp in the filename.

This process should also maintain/rotate the existing db backups.
Rules:
- keep the latest 5 db exports, regardless of timestamp
- keep the latest db backup generated for each week (sunday - saturday period), for the last 4 weeks
- keep the latest db backup generated for each month (first day of month - last day of month), for the last 12 months
- move all other db backups to an archive folder
- delete all db backups in the archive folder that are older than 12 months.

There should be two independent utility classes used to manage backups in the /api service:
- class that creates the backup (probably through pg_dump)
- class that manages the existing backups

## Prerequisites:
- understand the database schema of the project
- /api/backups folder should be used for the backups
- a /api/backups/archive folder should be used as the archive folder.
- understand the command that exits CLI application
- write an API endpoint that launches the db backup and management processes.  choose a request type that is most appropriate

## Process:
- user exits the CLI application
- CLI application calls a /db-backup API endpoint
- the API runs the process to manage existing backups, then the process to create a new backup.
- application exits normally.

## Testing:
- test that a new backup is created in the /api/backups folder
- make sure that the newly created backup contains both schema and data for each folder in the db.
- Create a series of fake db backup files that spans the previous 16 months.  after running process to manage existing backups, the retained files should follow the `Rules` defined in the `Context` section of this file.