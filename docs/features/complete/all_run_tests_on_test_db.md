# CLI/API/DB: Establish a test database and run all tests on that database

## Goal: The current tests are disrupting the application's database.  Create a test database that is safe to be used for running tests.

## Context/process
- the application database is being altered whenever tests run.  identify locations where any tests may connect to the application database
- the current application database should not be altered in any way when tests run
- tests in this project should never have the opportunity to even connect to the real application database
- the test database should be able to be destroyed or manipulated without risk of altering the application db
- make sure that all tests (cli, api, and db services) all run against the test database
