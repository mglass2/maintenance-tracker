# API: Utility to predict the current status of data used for interval tracking

## Goal: create a reusable utility class in the API service of the project that predicts the current status of any measurement used for tracking intervals (mileage, hours, etc.)

## Prerequisites/Inputs
- Input: item_id for the item being used for this prediction
- Input: the key for the type of prediction being made.  for example: `mileage` for a car.
- on the item.details field (JSONB), confirm that a json key called `forecast` exists.  
- the `forecast` key should subsequently contain a key for the type of measurement being used (example: `mileage` from the input).  In order to make a valid prediction, four child keys - start_date, start_measurement, reference_date, reference_measurement - are required and should also exist. the date keys should be dates and the measurement keys should be numerical.  think about the following example to help you understand:
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

## Calculation
- extract the four keys (start_date, start_measurement, reference_date, reference_measurement) under the type of prediction being made into variables to be used during the calculation.
- `ref_days_delta`: number of days between `start_date` and `reference_date`
- `cur_days_delta`: number of days between `reference_date` and the current date
- `ref_use_delta`: difference between `start_measurement` and `reference_measurement`
- `use_per_day` = `ref_use_delta` / `ref_days_delta`
- `predicted_measurement` = `reference_measurement` + (`use_per_day` * `cur_days_delta`)
- `predicted_measurement` (numerical) is the OUTPUT

## Test
Given the following, the prediction for `mileage` should be 730 on `2016-01-01`
```json
{
   "forecast":{
      "mileage":{
         "start_date":"2014-01-01",
         "start_measurement":0,
         "reference_date":"2015-01-01",
         "reference_measurement":365
      }
   }
}
```