"""Utility for predicting current interval tracking measurements."""

from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..models.item import Item
from ..services.exceptions import (
    InvalidForecastDataError,
    MissingForecastKeyError,
    ResourceNotFoundError,
)


class IntervalPredictor:
    """
    Predicts current measurement values for interval tracking.

    Uses linear interpolation based on historical data points stored in
    item.details.forecast to predict current values for measurements like
    mileage, hours, etc.

    Example forecast data structure in item.details:
    {
        "forecast": {
            "mileage": {
                "start_date": "2015-03-10",
                "start_measurement": 1000,
                "reference_date": "2021-05-15",
                "reference_measurement": 59000
            }
        }
    }
    """

    REQUIRED_FIELDS = [
        "start_date",
        "start_measurement",
        "reference_date",
        "reference_measurement",
    ]

    def __init__(self, db: Session):
        """
        Initialize the predictor with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def predict_current_value(
        self,
        item_id: int,
        measurement_key: str,
        prediction_date: Optional[date] = None,
    ) -> float:
        """
        Predict the current value for a measurement type.

        Args:
            item_id: ID of the item to predict for
            measurement_key: Type of measurement (e.g., "mileage", "hours")
            prediction_date: Date to predict for (defaults to today)

        Returns:
            Predicted measurement value as float

        Raises:
            ResourceNotFoundError: If item doesn't exist or is deleted
            InvalidForecastDataError: If forecast data is malformed or invalid
            MissingForecastKeyError: If measurement key not found in forecast
        """
        # Get the item
        item = self.db.query(Item).filter(Item.id == item_id, Item.is_deleted == False).first()

        if not item:
            raise ResourceNotFoundError(f"Item with ID {item_id} not found or is deleted")

        # Validate item has details
        if not item.details:
            raise InvalidForecastDataError(f"Item {item_id} has no details field")

        # Validate forecast exists
        if "forecast" not in item.details:
            raise InvalidForecastDataError(f"Item {item_id} details missing 'forecast' key")

        forecast = item.details["forecast"]

        # Validate measurement key exists
        if measurement_key not in forecast:
            raise MissingForecastKeyError(
                f"Measurement key '{measurement_key}' not found in forecast data. "
                f"Available keys: {list(forecast.keys())}"
            )

        measurement_data = forecast[measurement_key]

        # Validate required fields
        self._validate_forecast_structure(measurement_data, measurement_key)

        # Extract data
        start_date = self._parse_date(measurement_data["start_date"], "start_date")
        start_measurement = measurement_data["start_measurement"]
        reference_date = self._parse_date(measurement_data["reference_date"], "reference_date")
        reference_measurement = measurement_data["reference_measurement"]

        # Validate data values
        self._validate_forecast_values(
            start_date,
            start_measurement,
            reference_date,
            reference_measurement,
            measurement_key,
        )

        # Use provided date or default to today
        current_date = prediction_date or date.today()

        # Calculate prediction
        predicted_value = self._calculate_prediction(
            start_date,
            start_measurement,
            reference_date,
            reference_measurement,
            current_date,
        )

        return predicted_value

    def _validate_forecast_structure(
        self, data: Dict[str, Any], measurement_key: str
    ) -> None:
        """
        Validate that all required fields are present.

        Args:
            data: The forecast data dictionary for a measurement
            measurement_key: The measurement type being validated

        Raises:
            InvalidForecastDataError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise InvalidForecastDataError(
                f"Forecast data for '{measurement_key}' must be a dictionary"
            )

        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in data]

        if missing_fields:
            raise InvalidForecastDataError(
                f"Forecast data for '{measurement_key}' missing required fields: {missing_fields}. "
                f"Required: {self.REQUIRED_FIELDS}"
            )

    def _parse_date(self, date_value: Any, field_name: str) -> date:
        """
        Parse a date value from string or date object.

        Args:
            date_value: Value to parse (string or date)
            field_name: Name of the field (for error messages)

        Returns:
            Parsed date object

        Raises:
            InvalidForecastDataError: If date is invalid format
        """
        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError:
                raise InvalidForecastDataError(
                    f"Invalid date format for '{field_name}': '{date_value}'. "
                    "Expected format: YYYY-MM-DD"
                )

        raise InvalidForecastDataError(
            f"Field '{field_name}' must be a date string (YYYY-MM-DD) or date object, "
            f"got {type(date_value).__name__}"
        )

    def _validate_forecast_values(
        self,
        start_date: date,
        start_measurement: Any,
        reference_date: date,
        reference_measurement: Any,
        measurement_key: str,
    ) -> None:
        """
        Validate the values in forecast data.

        Args:
            start_date: Start date
            start_measurement: Start measurement value
            reference_date: Reference date
            reference_measurement: Reference measurement value
            measurement_key: Measurement type

        Raises:
            InvalidForecastDataError: If values are invalid
        """
        # Validate measurements are numeric
        if not isinstance(start_measurement, (int, float)):
            raise InvalidForecastDataError(
                f"start_measurement for '{measurement_key}' must be numeric, "
                f"got {type(start_measurement).__name__}"
            )

        if not isinstance(reference_measurement, (int, float)):
            raise InvalidForecastDataError(
                f"reference_measurement for '{measurement_key}' must be numeric, "
                f"got {type(reference_measurement).__name__}"
            )

        # Validate date ordering
        if reference_date <= start_date:
            raise InvalidForecastDataError(
                f"reference_date ({reference_date}) must be after start_date ({start_date})"
            )

        # Validate measurements are non-negative
        if start_measurement < 0:
            raise InvalidForecastDataError(
                f"start_measurement for '{measurement_key}' cannot be negative: {start_measurement}"
            )

        if reference_measurement < 0:
            raise InvalidForecastDataError(
                f"reference_measurement for '{measurement_key}' cannot be negative: {reference_measurement}"
            )

    def _calculate_prediction(
        self,
        start_date: date,
        start_measurement: float,
        reference_date: date,
        reference_measurement: float,
        current_date: date,
    ) -> float:
        """
        Calculate predicted measurement using linear interpolation.

        Args:
            start_date: Start date
            start_measurement: Measurement at start date
            reference_date: Reference date
            reference_measurement: Measurement at reference date
            current_date: Date to predict for

        Returns:
            Predicted measurement value
        """
        # Calculate days between dates
        ref_days_delta = (reference_date - start_date).days
        cur_days_delta = (current_date - reference_date).days

        # Calculate measurement change
        ref_use_delta = reference_measurement - start_measurement

        # Calculate rate of change per day
        use_per_day = ref_use_delta / ref_days_delta

        # Calculate predicted measurement
        predicted_measurement = reference_measurement + (use_per_day * cur_days_delta)

        return predicted_measurement
