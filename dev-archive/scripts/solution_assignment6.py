"""Assignment 6: factorial."""

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
        """Read integer from stdin.

        Input là số nguyên dương
        """
        return InputParser.safe_int(input().strip())


class FactorialService:
    """Factorial business logic."""

    @staticmethod
    def factorial(n: int) -> int:
        """Compute n! with loop.

        Phải dùng vòng lặp hoặc đệ quy tính giai thừa
        Xử lý n = 0 (kết quả = 1)
        """
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result


def normalize_number(n: int) -> int:
    """Clamp input to valid non-negative range."""
    if n < 0:
        return 0
    return n


def main() -> None:
    """Program entry point.

    Output là kết quả giai thừa
    """
    value = normalize_number(InputParser.read_number())
    print(FactorialService.factorial(value))


if __name__ == "__main__":
    main()
