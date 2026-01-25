"""Tests for TimeUnitConverter utility."""

import pytest

from utils.time_unit_converter import TimeUnitConverter


class TestTimeUnitConverterUnits:
    """Test that each unit in _UNITS converts to days correctly."""

    def test_convert_day_to_days(self):
        """Test that 1 day converts to 1 day."""
        result = TimeUnitConverter.convert(1, "day", "days")
        assert result == 1

    def test_convert_d_shorthand_to_days(self):
        """Test that 'd' shorthand converts correctly."""
        result = TimeUnitConverter.convert(1, "d", "days")
        assert result == 1

    def test_convert_days_plural_to_day(self):
        """Test that 'days' plural converts correctly."""
        result = TimeUnitConverter.convert(5, "days", "day")
        assert result == 5

    def test_convert_week_to_days(self):
        """Test that 1 week converts to 7 days."""
        result = TimeUnitConverter.convert(1, "week", "days")
        assert result == 7

    def test_convert_weeks_plural_to_days(self):
        """Test that 'weeks' plural converts to correct days."""
        result = TimeUnitConverter.convert(2, "weeks", "days")
        assert result == 14

    def test_convert_w_shorthand_to_days(self):
        """Test that 'w' shorthand converts correctly."""
        result = TimeUnitConverter.convert(3, "w", "days")
        assert result == 21

    def test_convert_year_to_days(self):
        """Test that 1 year converts to 365 days."""
        result = TimeUnitConverter.convert(1, "year", "days")
        assert result == 365

    def test_convert_years_plural_to_days(self):
        """Test that 'years' plural converts to correct days."""
        result = TimeUnitConverter.convert(2, "years", "days")
        assert result == 730

    def test_convert_y_shorthand_to_days(self):
        """Test that 'y' shorthand converts correctly."""
        result = TimeUnitConverter.convert(3, "y", "days")
        assert result == 1095

    def test_convert_days_to_week(self):
        """Test that 7 days converts to 1 week."""
        result = TimeUnitConverter.convert(7, "days", "week")
        assert result == 1

    def test_convert_days_to_weeks_rounded(self):
        """Test that 14 days converts to 2 weeks."""
        result = TimeUnitConverter.convert(14, "days", "weeks")
        assert result == 2

    def test_convert_days_to_year(self):
        """Test that 365 days converts to 1 year."""
        result = TimeUnitConverter.convert(365, "days", "year")
        assert result == 1

    def test_convert_days_to_years_rounded(self):
        """Test that 730 days converts to 2 years."""
        result = TimeUnitConverter.convert(730, "days", "years")
        assert result == 2

    def test_convert_week_to_year(self):
        """Test that weeks convert to years correctly."""
        result = TimeUnitConverter.convert(52, "weeks", "year")
        assert result == 1  # 52 weeks * 7 days/week = 364 days, 364/365 ~= 1 year

    def test_convert_year_to_week(self):
        """Test that 1 year converts to approximately 52 weeks."""
        result = TimeUnitConverter.convert(1, "year", "weeks")
        assert result == 52  # 365 days / 7 days/week = 52

    def test_convert_with_rounding(self):
        """Test that conversion results are properly rounded."""
        result = TimeUnitConverter.convert(10, "days", "weeks")
        assert result == 1  # 10/7 = 1.43, rounds to 1

    def test_convert_large_values(self):
        """Test conversion with large values."""
        result = TimeUnitConverter.convert(100, "years", "days")
        assert result == 36500


class TestTimeUnitConverterNormalize:
    """Test the _normalize method."""

    def test_normalize_lowercase_unit(self):
        """Test that lowercase units are normalized correctly."""
        result = TimeUnitConverter._normalize("day")
        assert result == "day"

    def test_normalize_uppercase_unit(self):
        """Test that uppercase units are converted to lowercase."""
        result = TimeUnitConverter._normalize("DAY")
        assert result == "day"

    def test_normalize_mixed_case_unit(self):
        """Test that mixed case units are converted to lowercase."""
        result = TimeUnitConverter._normalize("DaYs")
        assert result == "days"

    def test_normalize_with_whitespace(self):
        """Test that whitespace is stripped from units."""
        result = TimeUnitConverter._normalize("  week  ")
        assert result == "week"

    def test_normalize_invalid_unit_raises_error(self):
        """Test that invalid units raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TimeUnitConverter._normalize("months")
        assert "unsupported time unit" in str(exc_info.value).lower()

    def test_normalize_non_string_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError):
            TimeUnitConverter._normalize(123)

    def test_normalize_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            TimeUnitConverter._normalize("")

    def test_normalize_none_raises_error(self):
        """Test that None raises TypeError."""
        with pytest.raises(TypeError):
            TimeUnitConverter._normalize(None)


class TestTimeUnitConverterConvertInput:
    """Test the convert_input method for parsing user input."""

    def test_convert_input_with_unit(self):
        """Test parsing input with explicit unit."""
        result = TimeUnitConverter.convert_input("5 days", "days")
        assert result == 5

    def test_convert_input_no_space_before_unit(self):
        """Test parsing input with no space between number and unit."""
        result = TimeUnitConverter.convert_input("5days", "days")
        assert result == 5

    def test_convert_input_multiple_spaces(self):
        """Test parsing input with multiple spaces."""
        result = TimeUnitConverter.convert_input("5   days", "days")
        assert result == 5

    def test_convert_input_with_float_value(self):
        """Test parsing input with decimal value."""
        result = TimeUnitConverter.convert_input("2.5 weeks", "days")
        assert result == 14  # 2.5 truncates to 2, 2 * 7 = 14

    def test_convert_input_no_unit_defaults_to_days(self):
        """Test that input without unit defaults to days."""
        result = TimeUnitConverter.convert_input("10", "days")
        assert result == 10

    def test_convert_input_no_unit_converts_from_days(self):
        """Test that input without unit converts from days correctly."""
        result = TimeUnitConverter.convert_input("7", "weeks")
        assert result == 1

    def test_convert_input_uppercase_unit(self):
        """Test parsing input with uppercase unit."""
        result = TimeUnitConverter.convert_input("3 WEEKS", "days")
        assert result == 21

    def test_convert_input_mixed_case_unit(self):
        """Test parsing input with mixed case unit."""
        result = TimeUnitConverter.convert_input("1 WeEk", "days")
        assert result == 7

    def test_convert_input_short_unit(self):
        """Test parsing input with short unit notation."""
        result = TimeUnitConverter.convert_input("4 w", "days")
        assert result == 28

    def test_convert_input_y_shorthand(self):
        """Test parsing input with 'y' for year."""
        result = TimeUnitConverter.convert_input("2 y", "days")
        assert result == 730

    def test_convert_input_d_shorthand(self):
        """Test parsing input with 'd' for day."""
        result = TimeUnitConverter.convert_input("15 d", "days")
        assert result == 15

    def test_convert_input_leading_whitespace(self):
        """Test parsing input with leading whitespace."""
        result = TimeUnitConverter.convert_input("  5 days", "days")
        assert result == 5

    def test_convert_input_to_different_unit(self):
        """Test parsing and converting to a different unit."""
        result = TimeUnitConverter.convert_input("14 days", "weeks")
        assert result == 2

    def test_convert_input_year_to_days(self):
        """Test parsing year and converting to days."""
        result = TimeUnitConverter.convert_input("1 year", "days")
        assert result == 365

    def test_convert_input_invalid_format_no_number(self):
        """Test that input without number raises error."""
        with pytest.raises(ValueError) as exc_info:
            TimeUnitConverter.convert_input("days", "days")
        assert "invalid input format" in str(exc_info.value).lower()

    def test_convert_input_invalid_unit(self):
        """Test that invalid unit raises error."""
        with pytest.raises(ValueError) as exc_info:
            TimeUnitConverter.convert_input("5 days", "months")
        assert "unsupported time unit" in str(exc_info.value).lower()

    def test_convert_input_invalid_from_unit(self):
        """Test that invalid from_unit raises error."""
        with pytest.raises(ValueError) as exc_info:
            TimeUnitConverter.convert_input("5 hours", "days")
        assert "unsupported time unit" in str(exc_info.value).lower()

    def test_convert_input_zero_value(self):
        """Test parsing input with zero value."""
        result = TimeUnitConverter.convert_input("0 days", "days")
        assert result == 0

    def test_convert_input_large_value(self):
        """Test parsing input with large value."""
        result = TimeUnitConverter.convert_input("1000 days", "days")
        assert result == 1000

    def test_convert_input_fractional_decimal(self):
        """Test parsing input with fractional decimal."""
        result = TimeUnitConverter.convert_input("1.5 weeks", "days")
        assert result == 7  # 1.5 truncates to 1, 1 * 7 = 7

    def test_convert_input_only_number(self):
        """Test parsing input that is only a number."""
        result = TimeUnitConverter.convert_input("7", "days")
        assert result == 7

    def test_convert_input_week_to_year(self):
        """Test converting weeks to years."""
        result = TimeUnitConverter.convert_input("52 weeks", "years")
        assert result == 1

    def test_convert_input_preserves_rounding(self):
        """Test that rounding is applied correctly."""
        # 10 days / 7 = 1.43 weeks, should round to 1
        result = TimeUnitConverter.convert_input("10 days", "weeks")
        assert result == 1
