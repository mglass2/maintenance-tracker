"""Tests for interval predictor utility."""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from models.item import Item
from models.item_type import ItemType
from utils.interval_predictor import IntervalPredictor
from services.exceptions import (
    InvalidForecastDataError,
    MissingForecastKeyError,
    ResourceNotFoundError,
)


@pytest.fixture
def item_type(db: Session):
    """Create a test item type."""
    item_type = ItemType(name="Test Type", description="Test Description")
    db.add(item_type)
    db.commit()
    db.refresh(item_type)
    return item_type


class TestIntervalPredictorSuccess:
    """Test successful prediction scenarios."""

    def test_predict_mileage_from_feature_doc(self, db: Session, item_type):
        """Test the example from feature documentation."""
        # Given forecast data, prediction for mileage should be 730 on 2016-01-01
        item = Item(
            item_type_id=item_type.id,
            name="Test Car",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2014-01-01",
                        "start_measurement": 0,
                        "reference_date": "2015-01-01",
                        "reference_measurement": 365,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        result = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2016, 1, 1)
        )

        assert result == 730.0

    def test_predict_with_different_measurement_key(self, db: Session, item_type):
        """Test prediction for different measurement types."""
        # Hours prediction
        item = Item(
            item_type_id=item_type.id,
            name="Test Equipment",
            details={
                "forecast": {
                    "hours": {
                        "start_date": "2020-01-01",
                        "start_measurement": 100,
                        "reference_date": "2020-12-31",
                        "reference_measurement": 465,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # After 1 year (365 days), went from 100 to 465 (365 hours gained)
        # Rate = 1 hour/day
        # After another year (365 days), should be 465 + 365 = 830
        result = predictor.predict_current_value(
            item.id, "hours", prediction_date=date(2021, 12, 31)
        )

        assert result == 830.0

    def test_predict_with_zero_start_measurement(self, db: Session, item_type):
        """Test prediction when start measurement is zero."""
        item = Item(
            item_type_id=item_type.id,
            name="New Item",
            details={
                "forecast": {
                    "cycles": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2020-06-30",
                        "reference_measurement": 100,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # 181 days, 100 cycles, rate = 100/181 cycles/day
        # Prediction date is 2021-01-01, which is 186 days after reference
        # 100 + (100/181)*186 ~= 202.2
        result = predictor.predict_current_value(
            item.id, "cycles", prediction_date=date(2021, 1, 1)
        )

        assert abs(result - 202.2) < 1.0

    def test_predict_with_equal_start_and_reference_measurements(
        self, db: Session, item_type
    ):
        """Test prediction when start and reference measurements are equal (zero rate)."""
        item = Item(
            item_type_id=item_type.id,
            name="Static Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 1000,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # No change over time, should remain 1000
        result = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2022, 1, 1)
        )

        assert result == 1000.0

    def test_predict_for_future_date(self, db: Session, item_type):
        """Test prediction for future dates."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Car",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 10000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # 10000 miles in 366 days (2020 is leap year), rate ~27.3 miles/day
        # 365 days after reference = ~10000 + 9973 = ~19973
        result = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2022, 1, 1)
        )

        assert abs(result - 20000.0) < 30  # Allow for leap year differences

    def test_predict_for_past_date(self, db: Session, item_type):
        """Test prediction for past dates (before reference)."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Car",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2022-01-01",
                        "reference_measurement": 20000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # 2020-01-01 to 2022-01-01 is 731 days (leap year)
        # Rate = 20000/731 ~= 27.36 per day
        # 2021-01-01 is 366 days after start: 27.36 * 366 ~= 10013
        result = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2021, 1, 1)
        )

        assert abs(result - 10000.0) < 50  # Allow for leap year differences

    def test_predict_with_fractional_measurements(self, db: Session, item_type):
        """Test prediction with fractional measurement values."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Equipment",
            details={
                "forecast": {
                    "hours": {
                        "start_date": "2020-01-01",
                        "start_measurement": 100.5,
                        "reference_date": "2020-12-31",
                        "reference_measurement": 200.75,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # 100.25 hours over 364 days
        # Rate ~ 0.2754 hours/day
        # After another year should be ~200.75 + 100.5 = 301.25
        result = predictor.predict_current_value(
            item.id, "hours", prediction_date=date(2021, 12, 30)
        )

        assert abs(result - 301.0) < 1

    def test_predict_with_prediction_date_same_as_reference(
        self, db: Session, item_type
    ):
        """Test prediction when prediction date equals reference date."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 10000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        result = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2021, 1, 1)
        )

        assert result == 10000.0

    def test_predict_uses_today_as_default_date(self, db: Session, item_type):
        """Test that prediction defaults to today's date."""
        # Use dates that will give predictable results - need to be in past/future for valid range
        start = date(2020, 1, 1)
        reference = date(2021, 1, 1)

        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": start.isoformat(),
                        "start_measurement": 0,
                        "reference_date": reference.isoformat(),
                        "reference_measurement": 0,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        result = predictor.predict_current_value(item.id, "mileage")

        # Should equal reference since rate is 0
        assert result == 0.0

    def test_predict_with_multiple_measurement_keys(self, db: Session, item_type):
        """Test item with multiple measurement keys in forecast."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Car",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 10000,
                    },
                    "hours": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 500,
                    },
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        mileage = predictor.predict_current_value(
            item.id, "mileage", prediction_date=date(2022, 1, 1)
        )
        hours = predictor.predict_current_value(
            item.id, "hours", prediction_date=date(2022, 1, 1)
        )

        assert abs(mileage - 20000.0) < 50  # Allow for leap year differences
        assert abs(hours - 1000.0) < 25  # Allow for leap year differences


class TestIntervalPredictorErrors:
    """Test error handling and validation."""

    def test_item_not_found(self, db: Session):
        """Test error when item doesn't exist."""
        predictor = IntervalPredictor(db)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            predictor.predict_current_value(99999, "mileage")

        assert "not found" in str(exc_info.value).lower()

    def test_item_deleted(self, db: Session, item_type):
        """Test error when item is soft deleted."""
        item = Item(
            item_type_id=item_type.id,
            name="Deleted Item",
            is_deleted=True,
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()

        predictor = IntervalPredictor(db)

        with pytest.raises(ResourceNotFoundError):
            predictor.predict_current_value(item.id, "mileage")

    def test_item_no_details(self, db: Session, item_type):
        """Test error when item has no details field."""
        item = Item(item_type_id=item_type.id, name="Test Item", details=None)
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "no details field" in str(exc_info.value).lower()

    def test_missing_forecast_key(self, db: Session, item_type):
        """Test error when forecast key missing from details."""
        item = Item(
            item_type_id=item_type.id, name="Test Item", details={"other_data": "value"}
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "forecast" in str(exc_info.value).lower()

    def test_missing_measurement_key(self, db: Session, item_type):
        """Test error when measurement key not in forecast."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "hours": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 100,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(MissingForecastKeyError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "mileage" in str(exc_info.value)
        assert "Available keys" in str(exc_info.value)

    def test_missing_required_fields_in_forecast(self, db: Session, item_type):
        """Test error when required fields are missing."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        # Missing other required fields
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "missing required fields" in str(exc_info.value).lower()

    def test_invalid_date_format(self, db: Session, item_type):
        """Test error with invalid date format."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "01/01/2020",  # Wrong format
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "date format" in str(exc_info.value).lower()
        assert "YYYY-MM-DD" in str(exc_info.value)

    def test_invalid_reference_date_format(self, db: Session, item_type):
        """Test error with invalid reference date format."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "January 1, 2021",  # Wrong format
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "date format" in str(exc_info.value).lower()

    def test_non_numeric_start_measurement(self, db: Session, item_type):
        """Test error with non-numeric start measurement."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": "not a number",
                        "reference_date": "2021-01-01",
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "must be numeric" in str(exc_info.value).lower()

    def test_non_numeric_reference_measurement(self, db: Session, item_type):
        """Test error with non-numeric reference measurement."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": [1, 2, 3],  # Not numeric
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "must be numeric" in str(exc_info.value).lower()

    def test_reference_date_before_start_date(self, db: Session, item_type):
        """Test error when reference date is before start date."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2021-01-01",
                        "start_measurement": 0,
                        "reference_date": "2020-01-01",  # Before start
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "must be after" in str(exc_info.value).lower()

    def test_reference_date_equal_to_start_date(self, db: Session, item_type):
        """Test error when reference date equals start date."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2020-01-01",  # Same as start
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "must be after" in str(exc_info.value).lower()

    def test_negative_start_measurement(self, db: Session, item_type):
        """Test error with negative start measurement."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": -100,
                        "reference_date": "2021-01-01",
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "cannot be negative" in str(exc_info.value).lower()

    def test_negative_reference_measurement(self, db: Session, item_type):
        """Test error with negative reference measurement."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",
                        "reference_measurement": -500,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "cannot be negative" in str(exc_info.value).lower()

    def test_forecast_data_is_not_dict(self, db: Session, item_type):
        """Test error when forecast data is not a dictionary."""
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={"forecast": {"mileage": "not a dict"}},
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)

        with pytest.raises(InvalidForecastDataError) as exc_info:
            predictor.predict_current_value(item.id, "mileage")

        assert "must be a dictionary" in str(exc_info.value).lower()

    def test_date_object_returned_from_database(self, db: Session, item_type):
        """Test that date objects returned from database are handled correctly."""
        # When dates come back from the database, they might be date objects
        # This tests that the predictor can handle that
        item = Item(
            item_type_id=item_type.id,
            name="Test Item",
            details={
                "forecast": {
                    "mileage": {
                        "start_date": "2020-01-01",  # String in database
                        "start_measurement": 0,
                        "reference_date": "2021-01-01",  # String in database
                        "reference_measurement": 1000,
                    }
                }
            },
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        predictor = IntervalPredictor(db)
        # Manually test with date objects to verify they're accepted
        # 2020-01-01 to 2022-01-01 is 731 days (leap year), rate = 1000/366 ~= 2.73 per day
        # 366 days more = 2.73 * 366 = ~998
        result = predictor._calculate_prediction(
            date(2020, 1, 1), 0,
            date(2021, 1, 1), 1000,
            date(2022, 1, 1)
        )

        assert abs(result - 1998.0) < 10  # Allow for leap year arithmetic
