"""Assignment 2: calculate circle area."""

from typing import Final

PI: Final[float] = 3.14  # Sử dụng hằng số PI = 3.14


class InputParser:
    """Parses radius input."""

    @staticmethod
    def safe_float(text: str, default: float = 0.0) -> float:
        """Convert text to float safely.

        Có ép kiểu float cho bán kính
        """
        try:
            return float(text)
        except Exception:
            return default

    @staticmethod
    def read_radius() -> float:
        """Read radius from stdin."""
        return InputParser.safe_float(input().strip())


class CircleAreaService:
    """Business logic for area calculation."""

    @staticmethod
    def calculate(radius: float) -> float:
        """Return circle area by PI * r * r."""
        return PI * radius * radius


def format_number(value: float) -> str:
    """Format output as int when whole number."""
    if value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    """Program entry point."""
    radius = InputParser.read_radius()
    area = CircleAreaService.calculate(radius)
    print(format_number(area))


if __name__ == "__main__":
    main()
