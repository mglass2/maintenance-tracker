every time the user exits the application, export the entire database structure to a SQL file on a shared volume in docker.
timestamp the files
rules:
- keep the latest 5 db exports, regardless of timestamp
- keep the latest db backup generated for each week, for the last 4 weeks
- keep the latest db backup generated for each month, for the last 12 months
- delete all other db backups