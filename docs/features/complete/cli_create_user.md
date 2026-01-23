## CLI Command: create user

Consider the POST /users endpoint in the API service of this application.  Create an interactive CLI command in the CLI service of this application that:
- collects all necessary information from the operator of the application (currently name and email)
- calls the POST /users endpoint to submit the information from the operator
- waits for the response from the api and gives a confirmation message, either for the success or error of the call