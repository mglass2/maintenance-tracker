# CLI/API: Allow user to enter time intervals in days, weeks, years

## Goal: In every location where the CLI asks the user to enter a length of time in days, allow the user to enter the length of time in days, weeks, or years.

## Context:
- the class in api/src/utils/time_unit_converter.py provides functionality for converting user inputs for days/weeks/years.
- in relevant CLI commands, message users that they may enter in the format of 3d for days, 4w for weeks, or 1y for years. 
- don't alter the user input on the CLI side, perform the translation of time intervals inside the API.
- other aspects of the project expect the currently existing time intervals to be stored in days, do not alter the format in which we store time intervals in the db

## Prerequisites:
- identify the locations where the CLI service asks users to define an interval in days.
- identify the endpoints where the API service receives a time based interval in days.

## Process:
- accept in the user input of days/weeks/years
- process the user input into a numerical number of days using time_unit_converter.py
- save time intervals in days, which is the current behavior.  storing these intervals in the db should not change.

## Testing:
- for all the CLI locations where we ask the user to input a number of days, make sure that the messaging and input is updated to allow user to submit days/weeks/years
- for all the API endpoints that receive an interval in days, check that inputs of days, weeks, and years translates correctly to an integer number of days.