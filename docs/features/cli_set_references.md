# CLI: CLI command: set forecast information

## Goal: create a CLI command that populates the forecast structure for a type of measurement

## Context:
The following structure may exist in the item.details field.
```json
{
   "forecast":{
      "mileage":{
         "start_date":"2015-03-10",
         "start_measurement":1000,
         "reference_date":"2021-05-15",
         "reference_measurement":59000
      }
   }
}
```
the `forecast` key is static.  the type of forecast - in this case `mileage` (for an Automobile) - may change according to the item type.  There may also be multiple types of forecasts for a given item (mileage and engine_hours both apply to commercial vehicles, since they tend to engine idle a lot)

It may be necessary to make a new API endpoint to receive forecast information.  make a recommendation about the cleanest way to receive this information in the API.

## Prerequisites:
- consider the item table in the database
- consider the API endpoints for /items in the api service of the project

## Process:
- ask the user to select an item
- look at the item table and see if there is already any forecast structure setup in the `details` field
- ask the user if they would like to alter any current forecasts, or set up a new one.
- if the user chooses to alter a current forecast structure, allow the user to input start_date, start_measurement, reference_date, reference_measurement; and use the current values as the default for the user input of each.
- if the user chooses to create a new forecast structure, allow the user to input the type of forecast (`mileage` in the example above), then allow them to enter start_date, start_measurement, reference_date, reference_measurement.
- call the API endpoint for setting forecast information.

## Testing:
- test that submitting a new forecast structure works correctly
- test that updating an existing forecast structure works correctly
- test that multiple types of forecast is possible
- the start date MUST come before the reference date
- the start measurement MUST come before the reference measurement
