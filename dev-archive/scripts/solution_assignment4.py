"""Assignment 4: print sequence 1..n."""

from typing import Final


class InputParser:
    """Parses integer input for sequence."""

    @staticmethod
    def safe_int(text: str, default: int = 0) -> int:
        """Convert text to int safely."""
        try:
            return int(text)
        except Exception:
            return default

    @staticmethod
    def read_n() -> int:
        """Read n from stdin."""
        return InputParser.safe_int(input().strip())


class SequenceService:
    """Generates and prints number sequence."""

    @staticmethod
    def print_1_to_n(n: int) -> None:
        """Print numbers from 1 to n.

        Sử dụng vòng lặp for
        Sử dụng hàm range()
        """
        for i in range(1, n + 1):
            print(i)


def normalize_n(value: int) -> int:
    """Normalize n to non-negative integer."""
    if value < 0:
        return 0
    return value


def main() -> None:
    """Program entry point."""
    n = normalize_n(InputParser.read_n())
    SequenceService.print_1_to_n(n)


if __name__ == "__main__":
    main()
