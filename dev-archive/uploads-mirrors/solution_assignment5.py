"""Assignment 5: prime check."""

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

        Input là số nguyên từ stdin
        """
        return InputParser.safe_int(input().strip())


class PrimeService:
    """Prime checking business logic."""

    @staticmethod
    def is_prime(n: int) -> bool:
        """Check whether n is prime.

        Code phải có hàm kiểm tra nguyên tố
        Xử lý edge case: n <= 1
        """
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True


def format_result(is_prime_number: bool) -> str:
    """Return expected output token."""
    if is_prime_number:
        return "Yes"
    return "No"


def main() -> None:
    """Program entry point.

    Output "Yes" hoặc "No" đúng theo logic
    """
    number = InputParser.read_number()
    print(format_result(PrimeService.is_prime(number)))


if __name__ == "__main__":
    main()
