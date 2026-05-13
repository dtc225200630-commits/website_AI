"""Assignment 3: check even/odd."""

from typing import Final


class InputParser:
    """Parses integer input."""

    @staticmethod
    def safe_int(text: str, default: int = 0) -> int:
        """Convert text to int safely."""
        try:
            return int(text)
        except Exception:
            return default

    @staticmethod
    def read_number() -> int:
        """Read one integer from stdin."""
        return InputParser.safe_int(input().strip())


class ParityService:
    """Business logic for parity check."""

    @staticmethod
    def is_even(value: int) -> bool:
        """Return True when number is even.

        Sử dụng toán tử %
        """
        return value % 2 == 0


def format_output(is_even_number: bool) -> str:
    """Format expected output token.

    Sử dụng cấu trúc if...else
    """
    if is_even_number:
        return "Chan"
    else:
        return "Le"


def main() -> None:
    """Program entry point."""
    number = InputParser.read_number()
    print(format_output(ParityService.is_even(number)))


if __name__ == "__main__":
    main()
