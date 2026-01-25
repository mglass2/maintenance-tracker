
import re
from typing import Dict


class TimeUnitConverter:
    """
    Simple converter between time units.

    Public API:
        TimeUnitConverter.convert(1, "year", "days")      # -> 365
        TimeUnitConverter.convert_input("1 year", "days") # -> 365
    """

    _UNITS: Dict[str, int] = {
        # days base
        "d": 1,
        "day": 1,
        "days": 1,
        "w": 7,
        "week": 7,
        "weeks": 7,
        "y": 365,
        "year": 365,
        "years": 365,
    }

    @classmethod
    def convert(cls, value: int, from_unit: str, to_unit: str) -> int:
        """
        Convert value from one time unit to another.

        Args:
            value: The numeric value to convert
            from_unit: The source time unit (e.g., "days", "weeks", "years")
            to_unit: The target time unit (e.g., "days", "weeks", "years")

        Returns:
            The converted value as an integer (rounded)

        Raises:
            ValueError: If from_unit or to_unit is not supported
            TypeError: If from_unit or to_unit is not a string
        """
        from_normalized = cls._normalize(from_unit)
        to_normalized = cls._normalize(to_unit)
        return cls._convert_internal(value, from_normalized, to_normalized)

    @classmethod
    def convert_input(cls, input: str, to_unit: str) -> int:
        """
        Convert a string user input to a given number of `to_unit`.
        Returns an int.
        """

        # validate the to_unit is allowed and use the cleaned version
        to = cls._normalize(to_unit)

        # extract numerical portion of input (value)
        # extract non-numerical portion of input (from_unit)
        match = re.match(r'^(\d+(?:\.\d+)?)\s*(.*)$', input.strip())
        if not match:
            raise ValueError(f"invalid input format: {input!r}")

        value = int(float(match.group(1)))
        from_unit = match.group(2).strip() or "days"

        # clean the from_unit
        frm = cls._normalize(from_unit)

        # convert from_unit -> to_unit and return rounded int
        return cls._convert_internal(value, frm, to)



    @classmethod
    def _normalize(cls, unit: str) -> str:
        if not isinstance(unit, str):
            raise TypeError("unit must be a string")
        key = unit.strip().lower()
        if key not in cls._UNITS:
            raise ValueError(f"unsupported time unit: {unit!r}")
        return key

    @classmethod
    def _convert_internal(cls, value: int, from_unit: str, to_unit: str) -> int:
        """
        Internal conversion with pre-normalized units.

        This method expects from_unit and to_unit to already be normalized.
        It performs the actual conversion calculation without redundant normalization.

        Args:
            value: The numeric value to convert
            from_unit: Pre-normalized source unit
            to_unit: Pre-normalized target unit

        Returns:
            The converted value as an integer (rounded)
        """
        frm = cls._UNITS[from_unit]
        to = cls._UNITS[to_unit]
        return (float(value) * (frm / to)).__round__()
