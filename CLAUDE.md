# Dictionary

Consider the following language shortcuts when reading documentation about this project.
- "task" = maintenance task

# Project Description

The maintenance tracker application allows the user to record a history of maintenance tasks performed on items that the user owns.  The application also forecasts the future schedule of when different types of tasks
need to be performed on that item.  Ultimately, the user should be able to see the history of maintenance on each item, and also a forecast of when future maintenance items need to be performed.  

# Tech Stack/Details

## Assumptions

Use open source, permissively licensed software for this project.  you may not use software that requires
a subscription or fee of any kind.

Each service within this application should be containerized/encapsulated using docker, and orchestrated 
through docker-compose.

CLI services within this application should be written in python.

API services within this application should be written in python.

DB services within this application should be postgresql


## Application Layers/Services

cli: the interface that the user interacts with to use the application.  cli makes calls to the api service
api: the layer that 1: manages application logic, 2: receives requests from the cli layer based on user inputs, performs reads/writes to the db layer.
db: data storage for this application.

## Security considerations

This application will be run locally on the user's personal computer.  do not include security measures at this time for the cli or api layers.  include normal database security practices for the db layer.
